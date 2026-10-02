// static/js/crop_tool.js
//
// Crop-tool controller.
//
// Scans for input.crop-tool-target and, on file selection, opens a
// Cropper.js modal. On confirm, replaces the input's File with the
// cropped blob via DataTransfer. On "Use Original" or cancel, leaves
// the original File in place.
//
// Design notes:
//   * The modal (#crop-modal) is a single DOM node shared by all
//     crop-tool inputs on the page. state.input tracks the active one.
//   * PNG is used as the intermediate format; the Django pipeline
//     re-encodes to WebP at Q82 / max 1600px. The filename is suffixed
//     with ".crop" so the pipeline's _swap_extension produces
//     "foo.crop.webp" rather than clobbering a same-name sibling.
//   * No client-side downscale. One place enforces max dimension:
//     core.image_utils.optimize_image.
//   * Delegated listeners on document so the modal survives HTMX swaps
//     of the surrounding panel.

import Cropper from 'cropperjs';
import 'cropperjs/dist/cropper.css';

// ──────────────────────────────────────────────────────────────
// State
// ──────────────────────────────────────────────────────────────

const state = {
  input: null,           // the <input type="file"> that opened the modal
  originalFile: null,    // its File before any crop
  cropper: null,         // Cropper.js instance
  previewAspect: 4 / 3,  // currently selected ratio
  objectUrl: null,       // the object URL we created for the preview
};

// ──────────────────────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────────────────────

function getModal() {
  return document.getElementById('crop-modal');
}

function getCropperImage() {
  return document.getElementById('crop-image');
}

function getRatioBar() {
  return document.getElementById('crop-ratio-bar');
}

function parsePresets(raw) {
  // "1:1,4:3,free" -> ["1:1", "4:3", "free"]
  return (raw || '1:1,4:3,free')
    .split(',')
    .map(s => s.trim())
    .filter(Boolean);
}

function ratioLabel(r) {
  if (r === 'free') return '自由｜Free';
  return r;
}

function ratioValue(r) {
  // Returns the number Cropper expects, or NaN for free
  if (r === 'free') return NaN;
  const [w, h] = r.split(':').map(Number);
  if (!w || !h) return NaN;
  return w / h;
}

function formatBytes(n) {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(0)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

function readAsObjectUrl(file) {
  return URL.createObjectURL(file);
}

function revokeObjectUrl(url) {
  if (url) {
    try { URL.revokeObjectURL(url); } catch (_) { /* ignore */ }
  }
}

// ──────────────────────────────────────────────────────────────
// Modal lifecycle
// ──────────────────────────────────────────────────────────────

function buildRatioBar(input, presets, defaultRatio) {
  const bar = getRatioBar();
  if (!bar) return;
  bar.innerHTML = '';

  presets.forEach(preset => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.dataset.cropRatio = preset;
    btn.className = 'btn btn-xs btn-outline rounded-lg';
    if (preset === defaultRatio) {
      btn.classList.remove('btn-outline');
      btn.classList.add('btn-primary');
    }
    btn.textContent = ratioLabel(preset);
    bar.appendChild(btn);
  });
}

function applyRatio(ratio) {
  if (!state.cropper) return;
  const v = ratioValue(ratio);
  if (Number.isNaN(v)) {
    // Free: unlock the aspect ratio
    state.cropper.setAspectRatio(NaN);
  } else {
    state.cropper.setAspectRatio(v);
  }
  state.previewAspect = Number.isNaN(v) ? state.previewAspect : v;

  // Update button active state
  const bar = getRatioBar();
  if (bar) {
    bar.querySelectorAll('button[data-crop-ratio]').forEach(b => {
      const isActive = b.dataset.cropRatio === ratio;
      b.classList.toggle('btn-primary', isActive);
      b.classList.toggle('btn-outline', !isActive);
    });
  }
}

function openModalFor(input) {
  const file = input.files && input.files[0];
  if (!file) return;

  const modal = getModal();
  const img = getCropperImage();
  if (!modal || !img) return;

  // Reset state
  state.input = input;
  state.originalFile = file;
  state.previewAspect = 4 / 3;

  // Filename line
  const filenameEl = document.getElementById('crop-modal-filename');
  if (filenameEl) {
    filenameEl.textContent = `${file.name} · ${formatBytes(file.size)}`;
  }

  // Build ratio bar from the input's data attributes
  const presets = parsePresets(input.dataset.cropPresets);
  const defaultRatio = input.dataset.cropDefault || '4:3';
  buildRatioBar(input, presets, defaultRatio);

  // Load the image into the cropper
  revokeObjectUrl(state.objectUrl);
  state.objectUrl = readAsObjectUrl(file);
  img.src = state.objectUrl;

  // Destroy any previous Cropper instance
  if (state.cropper) {
    try { state.cropper.destroy(); } catch (_) { /* ignore */ }
    state.cropper = null;
  }

  const onImageLoad = () => {
    img.removeEventListener('load', onImageLoad);

    const initialRatio = ratioValue(defaultRatio);
    state.cropper = new Cropper(img, {
      aspectRatio: Number.isNaN(initialRatio) ? NaN : initialRatio,
      viewMode: 1,
      autoCropArea: 0.9,
      background: false,
      responsive: true,
      checkOrientation: true,
      modal: true,
      guides: true,
      center: true,
      highlight: false,
      cropBoxMovable: true,
      cropBoxResizable: true,
    });

    // Sync the active button state after Cropper mounts
    applyRatio(defaultRatio);
  };

  if (img.complete && img.naturalWidth > 0) {
    onImageLoad();
  } else {
    img.addEventListener('load', onImageLoad);
  }

  modal.showModal();
}

function closeModal({ restoreOriginal = false } = {}) {
  const modal = getModal();
  const img = getCropperImage();

  if (state.cropper) {
    try { state.cropper.destroy(); } catch (_) { /* ignore */ }
    state.cropper = null;
  }

  if (img) {
    img.removeAttribute('src');
  }

  revokeObjectUrl(state.objectUrl);
  state.objectUrl = null;

  if (restoreOriginal && state.input && state.originalFile) {
    // The original file is still in input.files — nothing to do.
    // Kept for symmetry / future-proofing.
  }

  state.input = null;
  state.originalFile = null;

  if (modal && modal.open) {
    modal.close();
  }
}

// ──────────────────────────────────────────────────────────────
// Commit
// ──────────────────────────────────────────────────────────────

function commitCrop() {
  if (!state.cropper || !state.input || !state.originalFile) return;

  const canvas = state.cropper.getCroppedCanvas({
    // No maxWidth/maxHeight: the server-side pipeline enforces max_dimension.
    imageSmoothingEnabled: true,
    imageSmoothingQuality: 'high',
  });

  if (!canvas) {
    console.warn('crop_tool: getCroppedCanvas returned null');
    return;
  }

  canvas.toBlob((blob) => {
    if (!blob) {
      console.warn('crop_tool: toBlob returned null');
      return;
    }

    const original = state.originalFile;
    const dot = original.name.lastIndexOf('.');
    const base = dot >= 0 ? original.name.slice(0, dot) : original.name;
    // Always emit .png so the pipeline sees a lossless intermediate.
    // Name format: "<base>.crop.png" -> pipeline produces "<base>.crop.webp"
    const newName = `${base}.crop.png`;

    const croppedFile = new File([blob], newName, {
      type: 'image/png',
      lastModified: Date.now(),
    });

    const dt = new DataTransfer();
    dt.items.add(croppedFile);

    state.input.files = dt.files;

    // Fire a custom event so any future listeners (e.g. live previews)
    // can react to the swap. There are none today, but it's cheap.
    state.input.dispatchEvent(new CustomEvent('crop:committed', {
      bubbles: true,
      detail: { file: croppedFile, originalFile: original },
    }));

    closeModal();
  }, 'image/png');
}

// ──────────────────────────────────────────────────────────────
// Event wiring
// ──────────────────────────────────────────────────────────────

function bindInputs() {
  document.querySelectorAll('input.crop-tool-target').forEach((input) => {
    if (input.dataset.cropBound === '1') return;
    input.dataset.cropBound = '1';
    input.addEventListener('change', () => {
      if (input.files && input.files.length) {
        openModalFor(input);
      }
    });
  });
}

function bindModalDelegates() {
  // Ratio preset clicks
  document.addEventListener('click', (e) => {
    const ratioBtn = e.target.closest('#crop-ratio-bar button[data-crop-ratio]');
    if (ratioBtn) {
      e.preventDefault();
      applyRatio(ratioBtn.dataset.cropRatio);
      return;
    }

    const actionBtn = e.target.closest('[data-crop-action]');
    if (!actionBtn) return;

    // Only respond if the modal is the one currently open
    const modal = getModal();
    if (!modal || !modal.open) return;

    const action = actionBtn.dataset.cropAction;
    e.preventDefault();

    if (action === 'cancel') {
      closeModal({ restoreOriginal: true });
    } else if (action === 'original') {
      // "Skip Crop" — leave input.files as the original file.
      // The pipeline will still optimise it; only the crop step is skipped.
      closeModal({ restoreOriginal: true });
    } else if (action === 'confirm') {
      commitCrop();
    }
  });

  // Escape key on the dialog: treat as cancel
  const modal = getModal();
  if (modal && !modal.dataset.cropEscBound) {
    modal.dataset.cropEscBound = '1';
    modal.addEventListener('cancel', (e) => {
      // <dialog> fires 'cancel' when Esc is pressed. Prevent the default
      // close so our cleanup runs (Cropper destroy + URL revoke).
      e.preventDefault();
      closeModal({ restoreOriginal: true });
    });
  }
}

// ──────────────────────────────────────────────────────────────
// Init
// ──────────────────────────────────────────────────────────────

function init() {
  bindInputs();
  bindModalDelegates();
}

document.addEventListener('DOMContentLoaded', init);
document.addEventListener('htmx:afterSwap', init);

// Expose for manual re-init if ever needed
window.cropToolInit = init;