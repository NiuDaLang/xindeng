// main.js

// ============================================
// PERFORMANCE API PATCH (Google Maps startTime Fix)
// ============================================
(function patchPerformanceAPI() {
    // Store original methods
    const originalMethods = {};
    
    function applyPatch() {
        if (!window.performance) return;
        
        // Store originals once
        if (!originalMethods.getEntriesByType && window.performance.getEntriesByType) {
            originalMethods.getEntriesByType = window.performance.getEntriesByType.bind(window.performance);
        }
        if (!originalMethods.getEntriesByName && window.performance.getEntriesByName) {
            originalMethods.getEntriesByName = window.performance.getEntriesByName.bind(window.performance);
        }
        if (!originalMethods.getEntries && window.performance.getEntries) {
            originalMethods.getEntries = window.performance.getEntries.bind(window.performance);
        }
        
        // Patch getEntriesByType
        if (originalMethods.getEntriesByType) {
            window.performance.getEntriesByType = function(type) {
                try {
                    const entries = originalMethods.getEntriesByType(type);
                    return entries && entries.length > 0 ? entries : [];
                } catch (e) {
                    return [];
                }
            };
        }
        
        // Patch getEntriesByName
        if (originalMethods.getEntriesByName) {
            window.performance.getEntriesByName = function(name, type) {
                try {
                    const entries = originalMethods.getEntriesByName(name, type);
                    return entries && entries.length > 0 ? entries : [];
                } catch (e) {
                    return [];
                }
            };
        }
        
        // Patch getEntries
        if (originalMethods.getEntries) {
            window.performance.getEntries = function() {
                try {
                    const entries = originalMethods.getEntries();
                    return entries || [];
                } catch (e) {
                    return [];
                }
            };
        }
    }
    
    // Apply immediately
    applyPatch();
    
    // Re-apply after HTMX swaps (in case something resets it)
    document.addEventListener('htmx:afterSwap', function() {
        applyPatch();
    });
    
    // Re-apply when Google Maps might load
    document.addEventListener('DOMContentLoaded', function() {
        applyPatch();
    });
    
    // Expose for manual re-patching if needed
    window.repatchPerformanceAPI = applyPatch;
})();

// ============================================
// ERROR SUPPRESSION (Backup)
// ============================================
const originalConsoleError = console.error;
console.error = function(...args) {
    const errorMsg = args[0] ? String(args[0]) : '';
    
    if (
        errorMsg.includes('startTime') ||
        errorMsg.includes('reportAllChanges') ||
        errorMsg.includes('Cannot read properties of undefined') ||
        (errorMsg.includes('WebSocket connection') && errorMsg.includes('Back-Forward Cache'))
    ) {
        console.debug('🔇 Suppressed known error');
        return;
    }
    
    originalConsoleError.apply(console, args);
};

// Global error handler
window.addEventListener('error', function(e) {
    if (e.message && (
        e.message.includes('startTime') ||
        e.message.includes('reportAllChanges')
    )) {
        e.preventDefault();
        e.stopImmediatePropagation();
        return true;
    }
}, true);

// Unhandled rejection handler
window.addEventListener('unhandledrejection', function(e) {
    const reason = e.reason;
    if (reason && (
        (reason.message && reason.message.includes('startTime')) ||
        (typeof reason === 'string' && reason.includes('startTime'))
    )) {
        e.preventDefault();
        return true;
    }
});

// ============================================
// GOOGLE MAPS AUTOCCOMPLETE INTEGRATION
// ============================================
// This ensures Google Maps works correctly with HTMX-loaded content
window.initGoogleMapsAutocomplete = function(inputElement, options = {}) {
    if (!window.google || !window.google.maps || !window.google.maps.places) {
        console.warn('Google Maps not loaded yet');
        return null;
    }
    
    try {
        const autocomplete = new window.google.maps.places.Autocomplete(
            inputElement,
            options
        );
        
        // Add listener for place selection
        autocomplete.addListener('place_changed', function() {
            const place = autocomplete.getPlace();
            console.log('Place selected:', place);
        });
        
        return autocomplete;
    } catch (error) {
        console.error('Error initializing Google Autocomplete:', error);
        return null;
    }
};

import "@/css/main.css"

import "cally"
import Swal from 'sweetalert2'

import { firework } from "./firework"

import 'glightbox/dist/css/glightbox.min.css';
import GLightbox from 'glightbox';

import 'sharer.js'; 
import htmx from 'htmx.org';

// // HTMX
// // 1. Capture a clean reference to HTMX's internal logger
// const originalHtmxLogger = htmx.logger;

// // 2. Override the logger with a custom filter hook
// htmx.logger = function(elt, event, detail) {
//     // Check if the current error is a history-restoration OOB error
//     if (event === 'htmx:oobErrorNoTarget') {
//         // If detail.xhr is missing, it is a history popstate restoration event
//         if (!detail || detail.xhr === undefined) {
//             console.log("🤫 Muted false-positive HTMX out-of-band history error.");
//             return; // Exit early to prevent printing the default error to the console
//         }
//     }

//     // Pass all normal operations and genuine errors to the original logger
//     if (originalHtmxLogger) {
//         originalHtmxLogger(elt, event, detail);
//     }
// };

// // 3. Keep your custom event listener clean for catch-all handling if needed
// document.body.addEventListener('htmx:oobErrorNoTarget', function(evt) {
//     if (!evt.detail || !evt.detail.targetId || evt.detail.xhr === undefined) return;

//     console.error("--- GENUINE HTMX OOB TARGET ERROR CAUGHT ---");
//     console.error("Target ID:", evt.detail.targetId);
//     console.error("Content:", evt.detail.content);
// });

// Listen for the native popstate event (fires the instant a user hits the back button)
window.addEventListener('popstate', function() {
    // Override console.error temporarily to filter out the HTMX internal string
    console.error = function(...args) {
        const errorMsg = args[0] ? String(args[0]) : '';
        
        // Mute if it matches HTMX's signature error for missing out-of-band targets
        if (errorMsg.includes('htmx:oobErrorNoTarget')) {
            console.log("🤫 Muted false-positive HTMX out-of-band history log.");
            return; // Swallows the log completely
        }
        
        // Allow all other genuine errors to pass through normally
        originalConsoleError.apply(console, args);
    };

    // 3. Restore the native console behavior immediately after HTMX completes history rendering
    setTimeout(() => {
        console.error = originalConsoleError;
    }, 100); // 100ms is plenty of time for doSwap and restoreHistory execution frames
});

// ***** change navbar color on-scroll *****
let scrollTimer = null;
const header = document.querySelector("#navbar");
const logo_landscape = header.querySelector("#logo_landscape"); // Assumes your logo is an img tag inside #navbar
const logo_square = header.querySelector("#logo_square"); // Assumes your logo is an img tag inside #navbar
const canvasElem = document.querySelector("#canvas_wrapper"); // Using your wrapper ID
const footerElem = document.querySelector("footer");
const login_btn = document.querySelector("#login_btn")
const register_btn = document.querySelector("#register_btn")

// Configuration
const scrollThreshold = 100;
const normalLogo_landscape = "/static/images/logos/logo_full_landscape.svg";
const altLogo_landscape = "/static/images/logos/logo_full_landscape_light.svg";
const normalLogo_square = "/static/images/logos/logo_transparent.svg";
const altLogo_square = "/static/images/logos/logo_transparent_light.svg";


window.addEventListener('scroll', function() {
    if (!header) return;

    // --- Part A: Logic for scrolling vs. stopped ---
    // Clear the timer every time a scroll event fires
    header.classList.add('scrolled-background');
    clearTimeout(scrollTimer);

    // Set a timer to run when scrolling stops (200ms delay)
    scrollTimer = setTimeout(() => {
        // Only remove transparency if we aren't in the "bottom zone"
        if (!isAtBottomZone()) {
            header.classList.remove('scrolled-background');
        }
    }, 200);

    // --- Part B: Logic for Bottom Elements (Canvas & Footer) ---
    if (isAtBottomZone()) {
        header.classList.add('scrolled-background'); // Keep transparent
        logo_landscape.src = altLogo_landscape; // Change logo
        logo_square.src = altLogo_square; // Change logo
        header.classList.add('text-[var(--xindeng-light-color)]')
        if(login_btn && register_btn){
            login_btn.classList.remove("bg-gray-200", "text-gray-700")
            login_btn.classList.add("bg-transparent")
            register_btn.classList.remove("bg-neutral-content", "text-primary-content")
            register_btn.classList.add("bg-transparent")
        }
    } else {
        logo_landscape.src = normalLogo_landscape; // Revert logo
        logo_square.src = normalLogo_square; // Revert logo
        header.classList.remove('text-[var(--xindeng-light-color)]')
        if(login_btn && register_btn){
            login_btn.classList.add("bg-gray-200", "text-gray-700")
            login_btn.classList.remove("bg-transparent")
            register_btn.classList.add("bg-neutral-content", "text-primary-content")
            register_btn.classList.remove("bg-transparent")
        }
    }
}); 

// Helper function to check if Canvas or Footer is in view
function isAtBottomZone() {
    if(document.querySelector("#canvas_wrapper")){
        const canvasRect = canvasElem?.getBoundingClientRect();
        const footerRect = footerElem?.getBoundingClientRect();
    
        // Check if the top of the canvas has reached the top of the viewport
        // or if the footer is visible
        const canvasReached = canvasRect && canvasRect.top <= 100; 
        const footerReached = footerRect && footerRect.top <= window.innerHeight;
    
        return canvasReached || footerReached;
    } else {
        return false
    }
}

// ***** Glightbox (Product - Gallery) Engine Block *****
let dynamicLightbox = null; 
let base_data = []; 
let slides_data = []; 

function init_glightbox(target_slides) {
    const formatted_slides = target_slides.map(slide => {
        return {
            href: slide.href,
            title: slide.title || "",
            type: "image"
        };
    });

    if (dynamicLightbox) {
        try { dynamicLightbox.destroy(); } catch(e) {}
    }

    const main_contents = check_elements_exist(document, ".glight_main");
    dynamicLightbox = GLightbox({
        elements: formatted_slides,
        autoplayVideos: false,
        zoomable: true
    });

    dynamicLightbox.on('open', () => {
        if (main_contents) {
            main_contents.forEach(el => {
                el.setAttribute("inert", "");
                el.setAttribute("aria-hidden", "false");
            });
        }
    });
    dynamicLightbox.on('close', () => {
        if (main_contents) {
            main_contents.forEach(el => el.removeAttribute('inert'));
        }
    });    
}

function moveItem(array, fromIndex, toIndex) {
    const working = [...array];
    const [item] = working.splice(fromIndex, 1);
    working.splice(toIndex, 0, item);
    return working;
}

function updateThumbnailBorderHighlight(clickedIndex) {
    console.log("Highlighting Triggered for Index Marker:", clickedIndex);
    const containers = check_elements_exist(document, '#product_gallery_images .thumbnail-item');
    if (!containers) return;

    containers.forEach(container => {
        const itemIndex = container.getAttribute('data-index');
        
        if (String(itemIndex) === String(clickedIndex)) {
            // 🌟 Apply Milder Active Ring + Scale Styles
            container.classList.add('border-primary/60', 'ring-2', 'ring-primary/40', 'ring-offset-2', 'z-10', 'scale-[1.02]');
            container.classList.remove('border-base-200', 'opacity-60', 'hover:border-base-300');
            // Force full opacity for the clicked item
            container.style.opacity = '1'; 
        } else {
            // 🌟 Revert back to Standard Inactive States
            container.classList.remove('border-primary/60', 'ring-2', 'ring-primary/40', 'ring-offset-2', 'z-10', 'scale-[1.02]');
            container.classList.add('border-base-200', 'opacity-60');
            // Clean up inline styles so tailwind classes take back control
            container.style.opacity = ''; 
        }
    });
}

function handleThumbnailClickInteraction(clickedIndex, targetMainThumbnail, targetImgSrc, e) {
    if (e) e.preventDefault();
    if (targetMainThumbnail) targetMainThumbnail.src = targetImgSrc;
    updateThumbnailBorderHighlight(clickedIndex);

    if (base_data && base_data.length > 0) {
        slides_data = moveItem([...base_data], Number(clickedIndex), 0);
        init_glightbox(slides_data);
    }
}

function setupProductGalleryBindings() {
    console.log("Synchronizing interactive behaviors over fresh server template layers...");
    const galleryLink = document.getElementById('open-product-gallery');
    const target_main_thumb = document.querySelector("#main_thumbnail");
    const thumbnail_containers = check_elements_exist(document, "#product_gallery_images .thumbnail-item");

    if (!target_main_thumb || !thumbnail_containers) return;

    if (galleryLink) {
        galleryLink.removeEventListener('click', window.mainGalleryOpenHandler);
        window.mainGalleryOpenHandler = function(e) {
            e.preventDefault(); 
            if (dynamicLightbox) dynamicLightbox.open();
        };
        galleryLink.addEventListener('click', window.mainGalleryOpenHandler);
    }

    // Read image paths cleanly directly from the active DOM structures
    base_data = [];
    thumbnail_containers.forEach(container => {
        const index_marker = container.getAttribute("data-index");
        const img_el = container.querySelector("img");
        if (!img_el) return;

        base_data.push({ href: img_el.src, title: img_el.alt || "" });

        // Wipe away stale listeners to prevent stacked background triggers
        container.replaceWith(container.cloneNode(true));
        const fresh_container = document.querySelector(`#product_gallery_images .thumbnail-item[data-index="${index_marker}"]`);
        const fresh_img = fresh_container.querySelector("img");

        fresh_container.addEventListener("click", (e) => {
            handleThumbnailClickInteraction(index_marker, target_main_thumb, fresh_img.src, e);
        });
    });

    if (base_data.length > 0) {
        init_glightbox(base_data);
    }
}

// ============================================
// ARTISAN GALLERY LIGHTBOX
// Mirrors the Product-page pattern: explicit elements array, no selector scan.
// ============================================
let artisanDynamicLightbox = null;

function setupArtisanGalleryLightbox() {
    const container = document.querySelector('[data-artisan-gallery]');
    if (!container) return;

    const tiles = container.querySelectorAll('.gallery-tile');
    if (tiles.length === 0) return;

    // Build slides array
    const slides = [...tiles].map((tile) => {
        const href = tile.getAttribute('href');
        const descSelector = tile.getAttribute('data-desc-selector');
        const descEl = descSelector ? document.querySelector(descSelector) : null;
        return {
            href,
            type: 'image',
            title: '',
            description: descEl ? descEl.innerHTML.trim() : '',
        };
    });

    // Destroy previous
    if (artisanDynamicLightbox) {
        try { artisanDynamicLightbox.destroy(); } catch (e) {}
        artisanDynamicLightbox = null;
    }

    // Build fresh
    artisanDynamicLightbox = GLightbox({
        elements: slides,
        autoplayVideos: false,
        zoomable: true,
        loop: false,
        touchNavigation: true,
        descPosition: 'bottom',
    });

    // Wire up click listeners
    tiles.forEach((tile, index) => {
        const fresh = tile.cloneNode(true);
        tile.replaceWith(fresh);
        fresh.addEventListener('click', (e) => {
            e.preventDefault();
            fresh.blur(); 
            if (artisanDynamicLightbox) {
                artisanDynamicLightbox.openAt(index);
            }
        });
    });
}

// ── SINGLE set of listeners ──
document.addEventListener('DOMContentLoaded', setupArtisanGalleryLightbox);

document.addEventListener('htmx:afterSwap', (evt) => {
    if (evt.detail.target && evt.detail.target.id === 'artisan-gallery-region') {
        setupArtisanGalleryLightbox();
    }
});

document.addEventListener('click', (e) => {
    const productBtn = e.target.closest('.glightbox-view-product');
    if (productBtn) {
        e.preventDefault();
        const url = productBtn.dataset.productUrl;
        if (url) window.open(url, '_blank', 'noopener,noreferrer');
    }
});

window.setupArtisanGalleryLightbox = setupArtisanGalleryLightbox;
window._artisanGalleryLightbox = artisanDynamicLightbox;


// Initialize on baseline load entry
setupProductGalleryBindings();
document.addEventListener("DOMContentLoaded", setupProductGalleryBindings);

// Intercept out-of-band HTMX swaps to automatically re-bind listeners
document.addEventListener("htmx:afterSwap", function(evt) {
    const product_purchase_panel_exists = check_element_exist(document, "#product-purchase-panel")
    const product_images_exist = check_element_exist(document, "#product_images")

    if (product_purchase_panel_exists || product_images_exist) {
        if (evt.detail.target.id === "product-purchase-panel" || evt.detail.target.id === "product_images") {
            console.log('product images!!!!!')
            setupProductGalleryBindings();
        }
    }
});

// ***** Sharer.js *****
document.addEventListener('DOMContentLoaded', () => {
    if (window.Sharer) {
        window.Sharer.init();
    }
});


// ***** cally *****
const daysBetween = (date1String, date2String) => {
    var d1 = new Date(date1String);
    var d2 = new Date(date2String);
    return (d2-d1)/(1000*3600*24);
}

const datePicker = (el, el_name) => {
    const startDate = document.getElementById("cally1").innerText
    const endDate = document.getElementById("cally2").innerText
    const startDateDisplay = document.getElementById("callyDate1")
    const finishDateDisplay = document.getElementById("callyDate2")

    document.getElementById(el_name).innerText = el.value

    // pick start date
    if(el_name === "cally1") {
        finishDateDisplay.setAttribute("min", el.value)
    // pick finish date 
    } else if(el_name === "cally2") {
        startDateDisplay.setAttribute("max", el.value)
    }                
}

const resetDate = () => {
    document.getElementById("cally1").innerText = "開始日期"
    document.getElementById("cally2").innerText = "截止日期"
    const startDateDisplay = document.getElementById("callyDate1")
    const finishDateDisplay = document.getElementById("callyDate2")
    startDateDisplay.removeAttribute("max")
    finishDateDisplay.removeAttribute("min")
}

const searchArchive = () => {
    const startDate = document.getElementById("cally1").innerText
    const endDate = document.getElementById("cally2").innerText

    // if both dates are picked, check if start date is earlier than finish date
    if(startDate != "開始日期" && endDate != "截止日期"){
        console.log("ready")
        // api 
    } else {
        Swal.fire({
            title: "【開始】與【截止】日期都要選喔！",
            text: "單日的話請都選同一天",
            icon: "error"
        });
    }
}

// check if element(s) exist
function check_element_exist(doc, selector) {
    return doc.querySelector(selector);
}

function check_elements_exist(doc, selector) {
    const nodes = doc.querySelectorAll(selector);
    return nodes.length > 0 ? [...nodes] : null;
}

window.onload = function() { 
    const fireworkEl = document.querySelector(".firework_gl");
    
    if (fireworkEl) {
        try {
            firework();
            
            setTimeout(() => {
                Swal.fire({
                    title: "Click to fire｜點擊場景點燃🎆",
                    text: "🖱️Left Click to Drag Scene｜左鍵拖拽可觀看3D景色",
                    icon: "info"
                });
            }, 100);
        } catch (error) {
            console.error("Caught Three.js initialization failure:", error);
            
            Swal.fire({
                title: "WebGL Initialization Failed / WebGL 啟動失敗",
                icon: "warning",
                width: '600px',
                html: `
                <div style="text-align: left; font-size: 0.95rem; line-height: 1.5; font-family: sans-serif;">
                    <!-- English Instructions -->
                    <div style="margin-bottom: 15px; border-bottom: 1px dashed #ccc; padding-bottom: 15px;">
                        <strong style="color: #d33;">Desktop:</strong>
                        <ul style="margin: 5px 0 10px 20px; padding: 0;">
                            <li>Go to browser "Settings", search for <b>"Hardware Acceleration"</b>, toggle it <b>ON</b>, and restart your browser.</li>
                            <li>If using Incognito/Private mode, certain extensions might be blocking WebGL.</li>
                        </ul>
                        <strong style="color: #e67e22;">Mobile Devices:</strong>
                        <ul style="margin: 5px 0 0 20px; padding: 0;">
                            <li>Turn off <b>"Low Power Mode / Battery Saver"</b>, and close extra background applications or tabs to free up RAM.</li>
                            <li>If you are inside an in-app browser (Line, WeChat, FB), tap the menu icon and select <b>"Open in Browser"</b> (Safari or Chrome).</li>
                        </ul>
                    </div>
                            
                    <!-- Chinese Instructions -->
                    <div>
                        <strong style="color: #d33;">電腦版 (Desktop):</strong>
                        <ul style="margin: 5px 0 10px 20px; padding: 0;">
                            <li>請進入瀏覽器「設定」，搜尋<b>「硬體加速」</b>(Use graphics acceleration) 並將其<b>開啟</b>，隨後重啟瀏覽器。</li>
                            <li>若使用隱私模式或無痕視窗，部分擴充功能可能會阻擋 WebGL 運作。</li>
                        </ul>
                        <strong style="color: #e67e22;">手機版 (Mobile):</strong>
                        <ul style="margin: 5px 0 0 20px; padding: 0;">
                            <li>請關閉手機的<b>「省電模式」</b>，並關閉其他背景應用程式與網頁分頁以釋放記憶體。</li>
                            <li>若是在 Line / WeChat / FB 內建瀏覽器中開啟，請點擊右上角選擇<b>「在瀏覽器中開啟」</b>(如 Safari 或 Chrome)。</li>
                        </ul>
                    </div>
                </div>
                `,
                confirmButtonText: "Got it / 我知道了"
            });
        }
    }
};

// Number formatter
const formatter = new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2, // Ensure at least 2 digits (e.g., 50.10)
    maximumFractionDigits: 2, // Ensure no more than 2 digits (e.g., 1234.56)
    useGrouping: true // Ensure commas are used (e.g., 10,000)
});

// Currency formatter
function format_currency(el, value, currencyCode) {
    try {
        const formatter = new Intl.NumberFormat(currencyCode == "CNY" ? 'zh-CN' : navigator.language, {
            style: 'currency',
            currency: currencyCode,
        })
        el.textContent = formatter.format(value)
    } catch (e) {
        console.error('Formatting error: ', e)
    }
}

// Header Cart Update
const updateHeaderCartDetails = (items_count, items_total, cart_items) => {
    document.querySelector("#cart_count_icon").innerText = items_count;
    document.querySelector("#cart_count").innerText = `${items_count} Items`
    document.querySelector("#cart_sub_total").innerText = `CNY ${items_total}`

    const product_list_item_html = cart_items.map(item => `
            <li class="flex items-center justify-between bg-base-50/50 hover:bg-base-50 border border-base-200/30 rounded-xl p-1.5 transition-all duration-300 gap-2 group">
                <a href="${item.url}" class="flex items-center gap-3 min-w-0 flex-1 select-none">
                    <div class="w-10 h-10 xs:w-12 xs:h-12 rounded-lg overflow-hidden bg-base-200 border border-base-200/50 flex-shrink-0 relative">
                        <img src="${item.image_url}" alt="product thumbnail" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" loading="lazy">
                    </div>
                    <div class="flex flex-col min-w-0">
                        <span class="text-xs font-bold text-base-content/80 group-hover:text-primary transition-colors truncate">
                            ${item.product}
                        </span>
                        <span class="text-[9px] xs:text-[10px] font-mono text-base-content/40 tracking-tight truncate mt-0.5">
                            SKU: ${item.product_variation}
                        </span>
                    </div>
                </a>
                <div class="flex items-center gap-1 text-base-content/60 font-sans font-medium px-2 flex-shrink-0 text-right">
                    <span class="text-[10px] opacity-40">✕</span>
                    <span id="header_item_qty_${item.id}" class="text-xs font-mono font-bold text-base-content/80 bg-base-200/60 px-1.5 py-0.5 rounded-md min-w-[1.25rem] text-center">
                        ${item.quantity }
                    </span>
                </div>

            </li>
        `).join('')

            // <li class="flex hover:bg-base-200 transition-colors duration-300 ease-in-out rounded-2xl items-center mt-2">
                // <a href="${item.url}" class="flex flex-col flex-grow-0 items-start p-2">
                    // <span class="text-sm"><strong>${item.product}</strong></span>
                    // <span class="text-[0.65rem]">${item.product_variation}</span>
                    // <img src="${item.image_url}" alt="product image" class="rounded-e-4xl">
                // <a>
                // <div class="h-full flex gap-1 items-center mr-2">
                //     <span class="">X</span>
                //     <span id="header_item_qty_${item.id}" class="flex-grow-1">${item.quantity }</span>
                // </div>
            // </li>
    console.log("[updateHeaderCartDetails] cart_items: ", cart_items)

    const cart_items_list = document.querySelector("#cart_items_list")
    cart_items_list.innerHTML = product_list_item_html
}

// share function
const share_link = async (title, text, link) => {
    console.log("Sharing triggered:", { title, text, link });

    const shareData = {
        title: title,
        text: text,
        url: link,
    };

    // 📱 Native System Share Sheet Path (Mobile Safari, iOS/Android Chrome)
    if (navigator.share && navigator.canShare && navigator.canShare(shareData)) {
        try {
            await navigator.share(shareData);
            console.log('Successfully shared natively!');
        } catch (err) {
            // Ignore AbortError if the user simply closed their native share window
            if (err.name !== 'AbortError') {
                console.error('Native sharing exception caught:', err);
            }
        }
    } 
    // 💻 Desktop Web Browser Resilient Fallback Pass
    else {
        try {
            // Copy the product link directly to the user's system clipboard
            await navigator.clipboard.writeText(link);
            
            // 💡 Toggle an elegant custom sweetalert alert dialog popup notification
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: "Link Copied!｜連結已複製",
                    html: "Product link copied to clipboard successfully! Share it with your friends.<br><span class='text-xs opacity-60 mt-1 block font-sans'>商品專屬連結已複製到您的剪貼簿，趕快分享給好友吧！</span>",
                    icon: "success",
                    timer: 2500,
                    showConfirmButton: false,
                    customClass: { popup: 'rounded-2xl font-sans text-xs' }
                });
            } else {
                alert("Link copied to clipboard!｜連結已複製！");
            }
        } catch (clipboardErr) {
            console.error('Clipboard injection blocked:', clipboardErr);
        }
    }
}

// Delete Wishlist Item
function delete_wish(wishlist_wrapper_el, wish_item_el, sku_id){
    // delete wish_item_el
    wish_item_el.remove()

    // delete divider for that item, if exists
    const divider_element = check_element_exist(wishlist_wrapper_el, `#divider_${sku_id}` )
    if(divider_element) divider_element.remove()

    // remaining list items
    const wishlist_items_li_els = wishlist_wrapper_el.querySelectorAll("li")

    // if all wish_items have been deleted, remove all inner HTML from the wrapper
    if(wishlist_items_li_els.length === 0) {
        wishlist_wrapper_el.innerHTML = ''
    // if there are remaining items in wishlist
    } else if (wishlist_items_li_els.length > 0) {
        // get the last item and check if it has a divider
        const last_wish_item = wishlist_wrapper_el.querySelector('li:last-of-type');
        const last_wish_item_id = last_wish_item.id.replace("wish_item_", "") 
        // check if its next sibling is a divider, if so, delete it
        const last_divider = last_wish_item.nextElementSibling;
        if(last_divider && last_divider.id === `divider_${last_wish_item_id}`) {
            last_divider.remove()
        }         
    }
}

// fecth and get json data
async function post_and_fetch_data(url, headers, body){
    const res = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: body
    })
    // if(!res.ok) throw new Error('Data not found');
    if(res.status === 500) window.location.href = `/error/500/`;
    if(res.status === 404) window.location.href = `/error/404/`;
    
    return res.json()
}

/*************************  PAYPAL  **************************/ 
window.paypalSdkLoadingStarted = window.paypalSdkLoadingStarted || false;

function get_csrf_token() {
    // 1. Look for the hidden input node generated by the master token element template tag
    let csrf_element = document.querySelector("#global-js-csrf-token [name=csrfmiddlewaretoken]");
    
    // 2. Local fallback check against your manual transfer form inside place_order.html
    if (!csrf_element) {
        csrf_element = document.querySelector("[name=csrfmiddlewaretoken]");
    }
    
    // 🌟 THE FIX: Explicitly ensure we return the .value text string hash, not the DOM Node!
    if (csrf_element && csrf_element.value) {
        return csrf_element.value;
    }
    
    // 3. Fallback direct browser cookstring lookup pass if form inputs are missing entirely
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    if (match) {
        return match[1]; // Extract the capture capture string safely
    }
    
    console.error("🔒 Security Core Alert: Unable to resolve authorization credentials from current DOM layout.");
    return null;
}

async function createOrder() {
    const proforma_invoice_number = JSON.parse(document.getElementById('proforma_invoice_number').textContent);
    const foreign_currency_code = JSON.parse(document.getElementById('foreign_currency_code').textContent);
    const locked_rate = JSON.parse(document.getElementById('locked_rate').textContent);

    try {
        const url = `/orders/api/paypal/create_paypal_order/?invoice=${proforma_invoice_number}&foreign_currency_code=${foreign_currency_code}&locked_rate=${locked_rate}`;
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": get_csrf_token(),
                "Content-Type": "application/json",
                "mode": 'same-origin',
            }
        });
        
        // 🎯 INTERCEPT PIPELINE: Read JSON error dictionaries from non-200 responses
        if (!response.ok) {
            const error_data = await response.json();
            
            if (error_data.error_code === "OUT_OF_STOCK") {
                // Dispatch native custom event to your working errorMssg listener instantly
                const evt = new CustomEvent("errorMssg", {
                    detail: {
                        title: error_data.title,
                        text: error_data.text,
                        redirect_url: error_data.redirect_url
                    }
                });
                document.dispatchEvent(evt);
            } else {
                // Fallback catch for alternate system errors
                Swal.fire({
                    icon: 'error',
                    title: 'Validation Error｜驗證失敗',
                    text: error_data.error || 'An unexpected verification error occurred.',
                    confirmButtonText: 'OK',
                    confirmButtonColor: '#3085d6'
                });
            }
            // Throwing stops execution so paymentSession.start does not run
            throw new Error(error_data.error || "Stock allocation threshold reached.");
        }
        
        const response_data = await response.json();
        console.log("Database secured. Passing PayPal Order ID:", response_data.id);
        
        // 🎯 RETURN ALIGNMENT: Returns exactly what paymentSession.start expects
        return { orderId: response_data.id };
        
    } catch(error) {
        console.error("Failed to execute pre-flight creation sequence:", error);
        throw error;
    }
}

async function captureOrder(data) {
    const proforma_invoice_number = JSON.parse(document.getElementById('proforma_invoice_number').textContent);
    try {
        // 💡 FIXED: Appended missing invoice number parameter required by backend
        const url = `/orders/api/paypal/capture_paypal_order/?paypal_order_id=${data.orderId}&invoice=${proforma_invoice_number}`;
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": get_csrf_token(),
                "Content-Type": "application/json",
                "mode": 'same-origin',
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error("Failed to capture order");
        return await response.json();
    } catch (error) {
        console.error("Failed to capture order", error);
        throw error;
    }
}

// Fetch OAuth Token from your custom backend proxy gateway
async function getBrowserSafeClientToken() {
    const csrf_token = get_csrf_token();
    if (!csrf_token) return null;
    
    try {
        const response = await fetch("/orders/api/paypal/token/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrf_token,
                "Content-Type": "application/json",
            },
        });
        
        if (!response.ok) {
            console.error(`❌ Token Proxy Error: Server responded with status code ${response.status}`);
            return null;
        }
        
        const data = await response.json();
        // Failsafe check: Verify that access_token exists before passing data forward
        if (!data || !data.access_token) {
            console.error("❌ Token Mismatch: Backend payload returned without a valid access_token key.");
            return null;
        }
        
        return data;
    } catch (err) {
        console.error("❌ Network Failure: Unable to fetch gateway authorization token details:", err);
        return null;
    }
}

async function renderPayPalComponents(clientToken) {
    const paypalButton = document.getElementById("paypal_action_trigger");
    if (!paypalButton) return;

    const foreign_currency_code = JSON.parse(document.getElementById('foreign_currency_code').textContent);
    const country_code = JSON.parse(document.getElementById('country_code').textContent);

    try {
        const sdkInstance = await window.paypal.createInstance({
            clientToken: clientToken,
            components: ["paypal-payments"],
        });

        const methods = await sdkInstance.findEligibleMethods({
            currencyCode: foreign_currency_code,
            countryCode: country_code,
        });

        if (methods.isEligible("paypal")) {
            // 🌟 THE NET INTEGRATION FIX: Clear out the skeleton loader the millisecond PayPal verifies eligibility!
            const skeletonLoader = document.getElementById("paypal-loading-skeleton");
            const buttonsContainer = document.getElementById("paypal_btns");
            
            if (skeletonLoader) {
                skeletonLoader.remove(); // Removes the loader node out of the layout completely
                console.log("🔒 PayPal Braintree Instance Clear: Skeleton loader purged cleanly.");
            }
            
            if (buttonsContainer) {
                // Re-adjust boundaries to remove dashed borders and padding, letting your clean button button fit snugly
                buttonsContainer.classList.remove("min-h-[90px]", "p-4", "border-dashed", "bg-base-100/50");
                buttonsContainer.classList.add("min-h-0", "p-0", "border-0", "bg-transparent");
            }

            paypalButton.removeAttribute("hidden");
        }

        const paymentSession = sdkInstance.createPayPalOneTimePaymentSession({
            onApprove: async (data) => {
                console.log("Payment approved by buyer:", data);
                
                // 🔄 Visual Anchor: Show a non-dismissible loading block while our backend processes stock subtractions
                Swal.fire({
                    title: 'Processing Payment...｜正在處理支付',
                    text: 'Please do not close this window.｜請勿關閉此頁面。',
                    allowOutsideClick: false,
                    didOpen: () => { Swal.showLoading(); }
                });

                try {
                    const backendResult = await captureOrder(data);
                    
                    if (backendResult.status === "SUCCESS") {
                        // Close loading state and move cleanly to confirmation screen
                        Swal.close();
                        window.location.href = `/orders/order_complete/?order_number=${backendResult.order_number}&transaction_id=${backendResult.transaction_id}`;
                    } else {
                        // 🎯 SWAL Fallback for internal database error
                        Swal.fire({
                            icon: 'error',
                            title: 'Order Sync Failed｜訂單同步失敗',
                            text: 'Database validation failed. Please check your network or contact support.',
                            confirmButtonText: 'OK｜確定',
                            confirmButtonColor: '#3085d6'
                        });
                    }
                } catch (error) {
                    console.error("Payment capture execution exception:", error);
                    // 🎯 SWAL Fallback for pipeline capture connection exception
                    Swal.fire({
                        icon: 'error',
                        title: 'Capture Error｜捕獲交易失敗',
                        text: 'Unable to communicate with payment settlement gateway.',
                        confirmButtonText: 'Retry｜重試',
                        confirmButtonColor: '#3085d6'
                    });
                }
            },
            onCancel(data) { 
                console.log("Payment cancelled:", data); 
                // Optional: Gentle Toast alert for cancellations
                Swal.fire({
                    icon: 'info',
                    title: 'Cancelled｜已取消',
                    html: `
                        <div class="font-sans text-sm text-center">
                            <p class="font-bold">Payment has been cancelled.</p>
                            <p class="text-xs text-base-content/70 mt-1">支付已被取消。</p>
                        </div>
                    `,
                    timer: 3000,
                    showConfirmButton: false
                });
            },
            onError(error) { 
                console.error("PayPal system encounter exception error:", error); 
                
                // 🎯 FIX: Elegant SWAL replacement handling unexpected gateway failures
                Swal.fire({
                    icon: 'error',
                    title: 'Payment Exception｜支付遭遇異常',
                    html: `
                        <div class="text-left font-sans text-sm">
                            <p class="font-bold">An unexpected error occurred during the window handshake.</p>
                            <p class="text-xs text-base-content/70 mt-1">手續校驗失敗，可能由於信用卡受限或安全政策拦截。</p>
                        </div>
                    `,
                    confirmButtonText: 'Try Alternative Method｜更換支付方式',
                    confirmButtonColor: '#3085d6'
                });
            },
        });

        const cleanButton = paypalButton.cloneNode(true);
        paypalButton.parentNode.replaceChild(cleanButton, paypalButton);

        cleanButton.addEventListener("click", async (e) => {
            e.preventDefault();
            if (window.checkoutTimer && window.checkoutTimer.currencyExpired) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Rates Lapsed｜匯率過期',
                    text: 'Transaction halted. Please refresh to fetch current market parameters.',
                    confirmButtonText: 'Refresh｜刷新頁面',
                    confirmButtonColor: '#d33'
                }).then(() => {
                    window.location.reload();
                });
                return;
            }
            
            cleanButton.disabled = true;
            cleanButton.classList.add("btn-disabled", "opacity-50");
            
            try {
                console.log("Checking database inventory allocation tracks...");
                
                // 1. Fetch your backend wrapper payload data object
                const orderData = await createOrder(); 

                // 2. Extract the explicit property key 'orderId' text string 
                const payPalOrderIdString = orderData.orderId; 
                
                // 3: Wrap the tracking string inside a schema configuration object
                // inside an unresolved Promise to satisfy BOTH modern type validation gates!
                const wrappedConfigPromise = Promise.resolve({
                    orderId: payPalOrderIdString
                });
                
                console.log("Launching secure interface with unified configuration payload.");
                
                // 2. Pass the wrapped configuration Promise to clear the modern PayPal initialization rules
                await paymentSession.start({ presentationMode: "auto" }, wrappedConfigPromise);

            } catch (error) {
                console.error("PayPal initiation halted due to validation failure:", error);
            } finally {
                cleanButton.disabled = false;
                cleanButton.classList.remove("btn-disabled", "opacity-50");
            }
        });
    } catch (err) {
        console.error('PayPal Core Instance configuration assignment failed:', err);
    }
}

async function initializePayPalSDK() {
    // 💡 FIX: Check the browser URL parameters early.
    // If the active window is already on the order_complete page, exit immediately 
    // to prevent the PayPal framework from spinning up and throwing telemetry logs errors!
    const urlParams = new URLSearchParams(window.location.search);
    if (window.location.pathname.includes('order_complete') || urlParams.has('order_number')) {
        console.log("🏁 Order finalized page detected. Suppressing PayPal engine initialization loops.");
        return;
    }

    const containerExists = document.getElementById("paypal_btns");
    if (!containerExists) return;


    // 💡 CNY SAFEGUARD GUARD: Block initialization loops instantly if domestic currency is selected
    const foreign_currency_code = JSON.parse(document.getElementById('foreign_currency_code').textContent);
    // if (foreign_currency_code && foreign_currency_code.toUpperCase() === 'CNY') {
    //     console.log("🇨🇳 CNY active: Bypassing automated script mounting pipelines.");
    //     return;
    // }

    if (foreign_currency_code && foreign_currency_code.toUpperCase() === 'CNY') {
        console.log("🇨🇳 CNY active: Bypassing automated script mounting pipelines.");
        
        const skeletonLoader = document.getElementById("paypal-loading-skeleton");
        if (skeletonLoader) skeletonLoader.remove(); // Safely clear the spinner out of the way
        
        if (containerExists) {
            containerExists.classList.remove("min-h-[90px]", "p-4", "border-dashed", "bg-base-100/50");
            containerExists.classList.add("min-h-0", "p-0", "border-0", "bg-transparent");
        }
        return;
    }    

    if (window.paypal && typeof window.paypal.createInstance === "function") {
        console.log("♻️ PayPal Core SDK already present in window space. Re-rendering layouts...");
        if (!window.cachedPayPalClientToken) {
            const data = await getBrowserSafeClientToken();
            window.cachedPayPalClientToken = data.access_token;
        }
        await renderPayPalComponents(window.cachedPayPalClientToken);
        return;
    }
    
    if (window.paypalSdkLoadingStarted) return;
    window.paypalSdkLoadingStarted = true;

    try {
        const data = await getBrowserSafeClientToken();
        window.cachedPayPalClientToken = data.access_token;

        const script = document.createElement('script');
        script.src = "https://www.sandbox.paypal.com/web-sdk/v6/core";
        script.async = true;
        
        script.onload = async () => {
            console.log("✨ PayPal Web SDK v6 Core asset injected completely.");
            await renderPayPalComponents(window.cachedPayPalClientToken);
        };

        script.onerror = (error) => {
            console.error("Failed to load the PayPal JS SDK script", error);
            window.paypalSdkLoadingStarted = false;

            // 🌟 ERROR GUARD: Remove spinner if network drops to prevent frozen layouts
            const skeletonLoader = document.getElementById("paypal-loading-skeleton");
            if (skeletonLoader) skeletonLoader.remove();
        };

        document.body.appendChild(script);
    } catch (error) {
        console.error("Error during PayPal initialization:", error);
        window.paypalSdkLoadingStarted = false;

        const skeletonLoader = document.getElementById("paypal-loading-skeleton");
        if (skeletonLoader) skeletonLoader.remove();
    }
}

window.initializePayPalSDK = initializePayPalSDK;

document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("paypal_btns")) {
        window.initializePayPalSDK();
    }
});


/**
 * SWAL alerts 
 */
// SWAL - Error
document.addEventListener("noService", function(evt) {
    Swal.fire({
        title: evt.detail.title,
        text: evt.detail.message,
        icon: 'error',
        confirmButtonColor: '#3085d6',
        confirmButtonText: 'OK'
    });
});
document.addEventListener("errorMssg", function(evt) {
    Swal.fire({
        title: evt.detail.title,
        html: evt.detail.text,
        icon: 'error',
        confirmButtonColor: '#3085d6',
        confirmButtonText: 'OK'
    });
});
document.addEventListener("infoMssg", function(evt) {
    Swal.fire({
        title: evt.detail.title,
        html: evt.detail.html,
        icon: evt.detail.icon,
        confirmButtonColor: '#3EC3EE',
        showConfirmButton: true,
        confirmButtonText: 'OK',
    });
});
document.addEventListener("successMssg", function(evt) {
    Swal.fire({
        title: evt.detail.title,
        html: evt.detail.html,
        icon: evt.detail.icon,
        confirmButtonColor: '#A5DB86',
        showConfirmButton: false,
        timer: 5000
    });
});
document.body.addEventListener('showDapDisclaimer', (evt) => {
    Swal.fire({
        icon: 'info',
        iconColor: '#f59e0b', 
        title: `<div class="text-lg font-bold">${evt.detail.title_en}<br><span class="text-base font-semibold text-neutral-500">${evt.detail.title_zh}</span></div>`,
        html: `
            <div class="text-left text-sm space-y-4 max-h-60 overflow-y-auto px-1 py-2">
                <p class="text-neutral-700 leading-relaxed">${evt.detail.text_en}<strong>${evt.detail.text_en_bold}</strong></p>
                <div class="border-t border-dashed border-gray-200 my-2"></div>
                <p class="text-neutral-600 leading-relaxed font-sans">${evt.detail.text_zh}<strong>${evt.detail.text_zh_bold}</strong></p>
                <p class="text-neutral-400 text-xs text-center"><a href=${evt.detail.delivery_policy_link}>${evt.detail.delivery_policy_link_label}</a></p>
            </div>
        `,
        confirmButtonText: 'I Understand & Agree / 我明白並同意',
        confirmButtonColor: '#10b981', // Tailwind success emerald green
        allowOutsideClick: false, // Enforce acknowledgment
        allowEscapeKey: false,
        customClass: {
            // Adds padding to the bottom of the actions row (where the button sits)
            actions: 'pb-6' 
        }
    });
});

// document.body.addEventListener('triggerOutOfStockSwal', function(evt) {
//     console.log("📥 Out of Stock Event Detected! Payload:", evt.detail);
    
//     const payload = evt.detail; // Extract our custom payload dictionary object
    
//     if (typeof Swal !== 'undefined') {
//         Swal.fire({
//             title: payload.title,
//             text: payload.text,
//             icon: 'warning',
//             confirmButtonText: '返回購物車｜Return to Cart',
//             confirmButtonColor: '#3085d6',
//             allowOutsideClick: false,
//             allowEscapeKey: false
//         }).then((result) => {
//             if (result.isConfirmed) {
//                 // Instantly push the browser back to your cart view route
//                 window.location.href = payload.redirect_url;
//             }
//         });
//     } else {
//         // Fallback framework in case SWAL scripts are still initializing
//         alert(payload.text);
//         window.location.href = payload.redirect_url;
//     }
// });

// redirect
document.body.addEventListener('triggerLoginPrompt', function(evt) {
    const alertData = evt.detail;
    
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: alertData.title,
            html: alertData.text,
            icon: alertData.icon || 'info',
            confirmButtonText: 'Log In｜前往登入',
            confirmButtonColor: '#10b981',
            allowOutsideClick: false,
            allowEscapeKey: false
        }).then((result) => {
            if (result.isConfirmed && alertData.redirect_url) {
                // Smoothly route the browser window to your user login platform
                window.location.href = alertData.redirect_url;
            }
        });
    } else {
        alert("Account Already Exists｜帳號已存在\n\n" + alertData.text.replace(/<br>/g, '\n'));
        if (alertData.redirect_url) window.location.href = alertData.redirect_url;
    }
});

// SWAL general
function confirmAction(button, title, html, icon, show_cancel, confirm_btn_color, cancel_btn_color, confirm_btn_text, cancel_btn_text) {
    Swal.fire({
        title: title,
        html: html,
        icon: icon,
        showCancelButton: show_cancel,
        confirmButtonColor: confirm_btn_color, // Red for delete
        cancelButtonColor: cancel_btn_color,
        confirmButtonText: confirm_btn_text,
        cancelButtonText: cancel_btn_text
    }).then((result) => {
        if (result.isConfirmed) {
            // Manually trigger the HTMX request
            htmx.trigger(button, 'confirmed');
        }
    })
}

/*************************  GOOGLE AUTO COMPLETE  **************************/ 
// call before init AutoComplete:
function preAutoComplete(){
    const originalAttachShadow = Element.prototype.attachShadow;
    Element.prototype.attachShadow = function(init) {
        // Intercept ONLY the Google Autocomplete component
        if (this.localName === 'gmp-place-autocomplete') {
            init.mode = 'open'; // Force it to be open
        }
        const shadowRoot = originalAttachShadow.call(this, init);

        // Inject the CSS directly into the component's internal root
        if (this.localName === 'gmp-place-autocomplete') {
            const style = document.createElement('style');
            style.textContent = `
                /* 1. Kills the blue focus ring div */
                .focus-ring { 
                    display: none !important; 
                    opacity: 0 !important;
                }
                /* 2. Kills the magnifier icon div */
                .autocomplete-icon { 
                    display: none !important; 
                }
                /* 3. Ensures the input fills the space and stays day-mode */
                input { 
                    padding-left: 12px !important; 
                    color: #333 !important;
                    background: transparent !important;
                    outline: none !important;
                    box-shadow: none !important;
                }
                /* Ensure no hover/active grey circles appear */
                .clear-button:hover, 
                .clear-button:active, 
                .clear-button:focus {
                    background-color: transparent !important;
                    background: none !important;
                }
                /* 1. Style the typed text and its position */
                input { 
                    padding-left: 15px !important; /* Adjust this to move the cursor/text */
                    font-size: 0.875rem !important;    /* Match your Django form font size */
                    font-family: var(--font-sans);
                    color: #333 !important;
                    background: transparent !important;
                    outline: none !important;
                }

                /* 2. SPECIFICALLY STYLE THE PLACEHOLDER */
                input::placeholder {
                    font-size: 0.75rem !important;    /* Make it slightly smaller if desired */
                    font-weight: 100 !important;
                    color: #9ca3af !important;     /* Gray color */
                    opacity: 1 !important;         /* Ensure it's fully visible */
                    font-weight: 400 !important;
                }
                
            `;
            shadowRoot.appendChild(style);
        }
        return shadowRoot;
    };
}

// init AutoComplete
async function initAutoComplete(form_id) {
    try {
        // ✅ Check if Google Maps is available
        if (typeof google === 'undefined' || !google.maps) {
            console.warn('Google Maps not available');
            return;
        }

        const { PlaceAutocompleteElement } = await google.maps.importLibrary("places");
        const { Place } = await google.maps.importLibrary("routes");
        
        const form = document.getElementById(form_id);
        if (!form) return;
        
        // ✅ Check if the address input exists
        const oldInput = form.querySelector('[id$="id_address_line_1"]');
        if (!oldInput || oldInput.tagName === 'GMP-PLACE-AUTOCOMPLETE') return;

        // ✅ CAPTURE THE ORIGINAL VALUE BEFORE REPLACING
        const initialValue = oldInput.value || '';
        console.log('Preserving initial address value:', initialValue);

        // Create and configure the New Web Component
        const allowedCountries = ["au", "nz", "jp", "kr", "tw", "hk", "mo", "sg", "my"]
        const autocomplete = new PlaceAutocompleteElement({
            includedRegionCodes: allowedCountries,
            includedPrimaryTypes: ["geocode"],
            componentRestrictions: { country: allowedCountries }
        });

        const hiddenAddressInput = document.createElement('input');
        hiddenAddressInput.type='hidden'
        hiddenAddressInput.name = 'address_line_1'
        hiddenAddressInput.id = 'hidden_address_line_1'
        form.appendChild(hiddenAddressInput)

        // avoid duplication of name
        if (oldInput) {
            // 1. STRIP THE NAME from the old element so it isn't sent in the POST
            oldInput.removeAttribute('name'); 
            
            // 2. ONLY the hidden input should have name="address_line_1"
            hiddenAddressInput.name = 'address_line_1';
        }

        autocomplete.removeAttribute('name')

        autocomplete.addEventListener("gmp-select", async (event) => {
            const prediction = event.placePrediction;
            if (!prediction) return;

            const place = await prediction.toPlace();
            // 1. MUST fetch 'id' and 'location' for Place ID and Lat/Lng
            await place.fetchFields({ fields: ["addressComponents", "displayName", "id", "location"] });

            // 2. Define target inputs FIRST (Fixes ReferenceError)
            const cityInput = form.querySelector('[id$="id_city"]');
            const stateInput = form.querySelector('[id$="id_state_province_region"]');
            const zipInput = form.querySelector('[id$="id_postal_code"]');
            const countrySelect = form.querySelector('[id$="id_country"]');
            const verifiedInput = form.querySelector('[id$="id_is_verified_by_google"]');
            const idInput = form.querySelector('[id$="id_google_place_id"]');
            const latInput = form.querySelector('[id$="id_latitude"]');
            const lngInput = form.querySelector('[id$="id_longitude"]');
            const line2Input = form.querySelector('[id$="id_address_line_2"]');
            const hiddenInput = form.querySelector('#hidden_address_line_1');

            if (place.id && idInput) {
                idInput.value = place.id;
                // SET VERIFIED TO TRUE
                if (verifiedInput) verifiedInput.value = "True"; 
            }

            // 3. Helper to get address components
            const getComp = (type, short = false) => {
                const c = place.addressComponents.find(c => c.types.includes(type));
                return c ? (short ? c.shortText : c.longText) : "";
            };

            // 4. Extract data
            const city = getComp("locality") || getComp("ward") || getComp("sublocality_level_1");
            const state = getComp("administrative_area_level_1");
            const country = getComp("country", true);
            const zip = getComp("postal_code");
            const addressLine1 = place.displayName || "";
            
            // Calculate Line 2
            const excludedTypes = ["locality", "ward", "sublocality_level_1", "administrative_area_level_1", "country", "postal_code"];
            const addressLine2 = place.addressComponents
                .filter(c => !c.types.some(type => excludedTypes.includes(type)))
                .map(c => c.longText)
                .reverse()
                .join(" ");

            // 5. Populate fields
            if (cityInput && !cityInput.readOnly) cityInput.value = city;
            if (stateInput && !stateInput.readOnly) stateInput.value = state;
            if (zipInput && !zipInput.readOnly) zipInput.value = zip;

            // Protect Country field from being overwritten if it is locked
            if (countrySelect && !countrySelect.hasAttribute('readonly') && !countrySelect.disabled) {
                countrySelect.value = country;
                // Trigger change event to keep your custom region UI logic synced
                countrySelect.dispatchEvent(new Event('change', { bubbles: true }));
            }
            if (line2Input && !line2Input.readOnly) line2Input.value = addressLine2;

            // Populate Google Metadata
            if (idInput) idInput.value = place.id || "";
            if (latInput) latInput.value = place.location?.lat().toFixed(6) || "";
            if (lngInput) lngInput.value = place.location?.lng().toFixed(6) || "";

            // 6. Update Address Line 1 and Sync
            if (hiddenInput) {
                hiddenInput.value = addressLine1;
                // This triggers your 'input' listeners to clear red errors
                hiddenInput.dispatchEvent(new Event('input', { bubbles: true }));
            }

            setTimeout(() => {
                autocomplete.value = addressLine1;
                // REMOVE name from the component again to be safe against re-renders
                autocomplete.removeAttribute('name');
            }, 1);

            // 🌟 ADD THIS BLOCK HERE: Force event bubbling & refresh the button state
            const filledFields = ['id_city', 'id_state_province_region', 'id_postal_code'];
            filledFields.forEach(fieldId => {
                const el = form.querySelector(`[id$="${fieldId}"]`);
                if (el) {
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });
            if (typeof window.updatePayButtonState === "function") window.updatePayButtonState();        
        });

        // Sync attributes so Django POST/HTMX works
        autocomplete.id = oldInput.id;
        autocomplete.name = "address_line_1";
        autocomplete.className = oldInput.className; 
        autocomplete.placeholder = oldInput.placeholder || "Input Address...｜輸入地址..."; 
        autocomplete.style.colorScheme = 'light';

        // ✅ SET THE VALUE BEFORE REPLACING
        if (initialValue) {
            autocomplete.value = initialValue;
        }

        // 3. Swap the elements
        oldInput.replaceWith(autocomplete);

        // ✅ AFTER REPLACEMENT, SYNC THE HIDDEN INPUT
        if (initialValue) {
            hiddenAddressInput.value = initialValue;
            
            // Also sync with the hidden input that has id
            const hiddenInput2 = form.querySelector('#id_address_line_1');
            if (hiddenInput2) {
                hiddenInput2.value = initialValue;
            }
        }

        // 4. Listener for manual clearing (when user backspaces or clicks 'X')
        // autocomplete.addEventListener('input', (e) => {
        //     const val = e.target.value;
        //     hiddenAddressInput.value = val

        //     if (!val) {
        //         hiddenAddressInput.value = '';
        //         // Remove error classes if they were added by a previous failed submit
        //         const wrapper = autocomplete.closest('label');
        //         wrapper?.classList.remove('border-error');
        //     }
        // });

        // Inside your autocomplete.addEventListener('input', ...
        autocomplete.addEventListener('input', (e) => {
            const val = e.target.value;

            // Find both variations of the hidden layout inputs securely
            const hiddenInput1 = form.querySelector('#hidden_address_line_1');
            const hiddenInput2 = form.querySelector('#id_address_line_1');
            
            if (hiddenInput1) hiddenInput1.value = val;
            if (hiddenInput2) hiddenInput2.value = val;

            // IF USER MANUALLY CHANGES TEXT, THEY ARE NO LONGER VERIFIED
            const verifiedInput = form.querySelector('[id$="id_is_verified_by_google"]');
            if (verifiedInput) verifiedInput.value = "False";

            if (!val) {
                // Clear Google data if input is wiped
                ['id_google_place_id', 'id_latitude', 'id_longitude'].forEach(suffix => {
                    const el = form.querySelector(`[id$="${suffix}"]`);
                    if (el) el.value = '';
                });

                // Force the hidden synced inputs to be absolutely blank strings
                if (hiddenInput1) hiddenInput1.value = '';
                if (hiddenInput2) hiddenInput2.value = '';
                
                const wrapper = autocomplete.closest('label');
                wrapper?.classList.remove('border-error');
            }

            // 🌟 FORCE AN IMMEDIATE RETRY ON THE VALIDATOR ENGINE
            if (typeof window.updatePayButtonState === "function") {
                window.updatePayButtonState();
            }
        });

        // 5. Enable BOTH manual and autocomplete
        autocomplete.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                // If the autocomplete dropdown is NOT open, allow the form to submit
                const pacContainer = document.querySelector('.pac-container');
                if (!pacContainer || pacContainer.style.display === 'none') {
                    // Let it submit manually
                    return;
                }
                // If dropdown IS open, prevent submit so user can select a place
                e.preventDefault();
            }
        });




    } catch (error) {
        // ✅ Catch and suppress Google Maps errors
        if (error && error.message && error.message.includes('startTime')) {
            console.warn('Google Maps performance tracking error suppressed');
            return;
        }
        console.error('initAutoComplete error: ', error)
    }
}

function initRegionLogic(form_id) {
    const form = document.getElementById(form_id)
    if (!form) return;

    // initial toggle on load
    toggleProvinceFields(form);

    // watch for country changes
    const countrySelect = form.querySelector('[name="country"]')
    if (countrySelect) {
        countrySelect.addEventListener('change', function() {
            toggleProvinceFields(form)
        })
    }

    const chinaProvinceSelect = document.querySelector('select[name="china_province"]');
    if (chinaProvinceSelect) {
        chinaProvinceSelect.addEventListener('change', function() {
            if (this.value) {
                // 1. Remove error class from the select itself
                this.classList.remove('select-error');
                // 2. Remove error styling from the parent label wrapper if it exists
                const wrapper = document.querySelector('.china_field_wrapper');
                if (wrapper) wrapper.classList.remove('border-error!', 'ring-error!');
                // 3. (Optional) Hide the error text message below it
                const errorLabel = wrapper?.nextElementSibling;
                if (errorLabel && errorLabel.classList.contains('label')) {
                    console.log("error label")
                    errorLabel.classList.add('hidden');
                }
            }
        });
    }
}

function toggleProvinceFields(form) {
    const country = form.querySelector('[name="country"]').value;
    const address1 = form.querySelector('[id$="id_address_line_1"]').value;
    const isChina = country === 'CN';
    const isFillingAddress = address1 && address1.trim() !== "";
    
    const chinaWrapper = form.querySelector('.china_field_wrapper');
    const regionWrapper = form.querySelector('.region_field_wrapper');
    
    if (chinaWrapper && regionWrapper) {
        chinaWrapper.classList.toggle('hidden', !isChina);
        regionWrapper.classList.toggle('hidden', isChina);

        // Dynamic Browser-Level Required toggle
        const chinaSelect = chinaWrapper.querySelector('select');
        const regionInput = regionWrapper.querySelector('input');

        if (chinaSelect) chinaSelect.required = (isChina && isFillingAddress);
        if (regionInput) regionInput.required = (!isChina && isFillingAddress);
    }
}

htmx.config.ignoreOobSwapErrors = true;

// ***** Reviews *****
// 🌟 SWEETALERT CONTROL INTERCEPT MANAGER FOR SECURE REVIEWS DELETIONS
function confirmSweetAlertDelete(reviewId) {
    if (typeof Swal === 'undefined') {
        // Fallback target action if SweetAlert bundles fail to initialize
        if (confirm("Are you sure you want to delete this review?\n確定要刪除此評價嗎？")) {
            const anchor = document.getElementById(`hidden_delete_trigger_anchor_${reviewId}`);
            if (anchor) htmx.trigger(anchor, "click");
        }
        return;
    }

    // 1. Dual-Language Modal Confirmation Prompt Layout
    Swal.fire({
        // 🌟 FIXED: Implemented Eg/Ch Title with block-isolated layouts
        title: "Are you sure you want to delete this review?<br><span class='text-xs font-sans tracking-normal opacity-50 block mt-1'>確定要刪除此評價嗎？</span>",
        // 🌟 FIXED: Swapped 'text' parameter for 'html' to style detailed sub-text elegantly
        html: `
            <div class="text-left space-y-1.5 opacity-70 border-t border-b border-base-200 py-3 my-2 font-sans leading-relaxed">
                <p class="text-[10px] opacity-60"><b>Warning:</b> Once deleted, this artwork feedback record and its attached images will be permanently removed from our database. This action cannot be undone.</p>
                <p><b>警告：</b>刪除後，此項藝術品反饋記錄與相關相片將從數據庫中永久消失，無法撤銷。</p>
            </div>
        `,
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "var(--color-primary, #111)",
        cancelButtonColor: "#d33",
        // 🌟 FIXED: Dual-Language Operation Buttons Shape
        confirmButtonText: "Yes, Delete｜確定刪除",
        cancelButtonText: "Cancel｜取消變更",
        background: "#ffffff",
        customClass: {
            popup: "font-sans text-xs rounded-xl border border-base-200 shadow-xl max-w-sm",
            title: "text-sm font-semibold font-serif tracking-widest text-neutral text-center leading-snug pt-2",
            confirmButton: "btn btn-xs btn-neutral rounded px-4 font-normal tracking-wide",
            cancelButton: "btn btn-xs btn-ghost rounded px-4 font-normal"
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const hiddenAnchor = document.getElementById(`hidden_delete_trigger_anchor_${reviewId}`);
            if (hiddenAnchor) {
                // Execute dynamic async deletion sweep parameters cleanly via HTMX
                htmx.trigger(hiddenAnchor, "click");
                
                // 2. Dual-Language Successful Action Dialogue Box
                Swal.fire({
                    // 🌟 FIXED: Eg/Ch Confirmation Complete Notification Layout
                    title: "Deleted Successfully｜已成功刪除",
                    html: `
                        <div class="text-center font-sans text-xs opacity-70 py-2">
                            <p class="text-[10px] opacity-60 mt-1">Your review record has been securely removed from our store database.</p>
                            <p>您的反饋記錄已從小店系統數據庫安全移除。</p>
                        </div>
                    `,
                    icon: "success",
                    confirmButtonColor: "var(--color-primary, #111)",
                    confirmButtonText: "Close｜關閉",
                    customClass: {
                        popup: "font-sans text-xs rounded-xl max-w-xs p-4",
                        title: "text-sm font-bold font-serif tracking-wide text-neutral pt-2",
                        confirmButton: "btn btn-xs btn-neutral rounded px-4 font-normal tracking-wide"
                    }
                });
            }
        }
    });
}

function openOrderDetailsModal(orderNumber) {
    const targetModal = document.getElementById(`modal_${orderNumber}`);
    if (targetModal) targetModal.showModal();
}

function closeOrderDetailsModal(orderNumber) {
    const targetModal = document.getElementById(`modal_${orderNumber}`);
    if (targetModal) targetModal.close();
}
// JavaScript cancellation routine handler function execution track
async function triggerOrderCancellation(orderNumber, totalDue, paidByVoucher, isSelfService) {
    const activeTokenString = window.get_csrf_token();
    
    // 🌟 THE RESOLUTION ANCHOR: Locate the active parent modal dialog element in the current DOM
    const targetModalContainer = document.getElementById(`modal_${orderNumber}`);
    
    // Fallback safely to document.body if target lookups omit nodes
    const swalMountTarget = targetModalContainer ? targetModalContainer : 'body';

    if (!activeTokenString) {
        Swal.fire({
            icon: 'error',
            title: 'Authorization Expired｜驗證權限失效',
            text: 'Security verification token length mismatch. Please reload your dashboard and try again.',
            target: swalMountTarget // 🌟 Scoped fail warning anchor
        });
        return;
    }

    // Displays confirmation prompt dialogues inside the modal layer, eliminating stack collisions
    const selection = await Swal.fire({
        title: 'Cancel Order?｜取消確認',
        text: `Are you sure you want to cancel Invoice #${orderNumber}? This action will release held item inventory pools.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, Cancel｜確認取消',
        cancelButtonText: 'No, Keep｜保留訂單',
        target: swalMountTarget // 🌟 Forces prompt overlay to stack perfectly on top of open dialogs
    });

    if (!selection.isConfirmed) return;

    // Display non-dismissible loading block while background thread transactions compile
    Swal.fire({
        title: 'Processing Cancellation...｜正在取消中',
        text: 'Please do not close this window.',
        allowOutsideClick: false,
        target: swalMountTarget, // 🌟 Keeps background spinner over open modal viewport bounds
        didOpen: () => { Swal.showLoading(); }
    });

    try {
        const refundTypeParam = (paidByVoucher === 'true') ? 'voucher' : 'cash';
        const url = `/orders/cancel_request/${orderNumber}/?refund_type=${refundTypeParam}`;
        
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": activeTokenString,
                "Content-Type": "application/json",
                "mode": 'same-origin'
            }
        });

        // 🌟 FIXED: Read json payload parameters to identify hidden 403 authorization failures
        const resultData = await response.json();

        if (response.ok && resultData.status === "SUCCESS") {
            Swal.fire({
                icon: 'success',
                title: 'Cancelled ｜ 變更成功',
                text: 'Order cancellation parameters processed successfully.',
                timer: 2000,
                showConfirmButton: false,
                target: swalMountTarget
            }).then(() => {
                if (targetModalContainer && typeof targetModalContainer.close === 'function') {
                    targetModalContainer.close();
                }
                if (window.htmx) {
                    htmx.ajax('GET', window.location.href, {target: '#orders_ledger_container', swap: 'innerHTML'});
                } else {
                    window.location.reload();
                }
            });
        } else {
            // Drop directly down to display actual target verification issue strings
            throw new Error(resultData.error || `Server verification dropped with status: ${response.status}`);
        }

    } catch (err) {
        console.error("Cancellation pipeline network exception encountered:", err);
        Swal.fire({
            icon: 'error',
            title: 'Action Blocked｜請求遭拒絕',
            text: 'Unable to authorize cancellation requests. This order profile may be locked or undergoing verification.',
            target: swalMountTarget // 🌟 Scoped exception display track
        });
    }
}

/**
 * Programmatic form submittal router to process data over secure POST channels.
 */
function executeSecurePostCancellation(orderNumber, refundType) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/orders/cancel_request/${orderNumber}/?refund_type=${refundType}`;

    const csrfToken = document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=');

    if (csrfToken) {
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);
    }

    document.body.appendChild(form);
    form.submit();
}


// Update sidebar active visual borders
// function updateActiveLink(element) {
//     console.log("update activate link")
//     if (!element) return;
//     const items = document.querySelectorAll('.dashboard-item');
//     items.forEach(li => li.classList.remove("is-active"));
//     if (!element.classList.contains('sidebar_link')) {
//         let link_type = element.id
//         console.log("link type: ", link_type)
//         switch (link_type) {
//             case "profile_header":
//             case "complete_profile":
//             case "edit_profile_label":
//             case "profile_faq_en":
//             case "profile_faq_cn":
//                 const edit_profile_li = document.querySelector("#edit_profile_li")
//                 edit_profile_li.classList.add("is-active")
//                 break;
//             case "addresses_header":
//             case "addresses":
//             case "address_book_label":
//                 const addresses_li = document.querySelector("#addresses_li")
//                 addresses_li.classList.add("is-active")
//                 break;
//             case "orders_header":
//             case "works_owned":
//                 const orders_li = document.querySelector("#orders_li")
//                 orders_li.classList.add("is-active")
//                 break;
//             case "offers_header":
//             case "perks_label":
//                 const perks_li = document.querySelector("#perks_li")
//                 perks_li.classList.add("is-active")
//                 break;
//             case "vouchers_header":
//             case "my_vouchers":
//                 const vouchers_li = document.querySelector("#vouchers_li")
//                 vouchers_li.classList.add("is-active")
//                 break;
//             case "wishlist_header":
//             case "wishlist_label":
//                 const wishlist_li = document.querySelector("#wishlist_li")
//                 wishlist_li.classList.add("is-active")
//                 break;
//             case "favorites_header":
//             case "favorites_label":
//                 const favorites_li = document.querySelector("#favorites_li")
//                 favorites_li.classList.add("is-active")
//                 break;
//             case "help_header":
//             case "helpdesk":
//             case "help_faq_en1":
//             case "help_faq_cn1":
//             case "help_faq_en2":
//             case "help_faq_cn2":
//             case (link_type.startsWith("order_")):
//                 const help_li = document.querySelector("#help_li")
//                 help_li.classList.add("is-active")
//                 break;
//             case "threed_header":
//             case "threed_label":
//                 const threed_li = document.querySelector("#threed_li")
//                 threed_li.classList.add("is-active")
//                 break;
//             default:
//                 const main_li = document.querySelector("#main_li")
//                 main_li.classList.add("is-active")
//         }
//     } else {
//         const parentLi = element.closest("li");
//         if (parentLi) {
//             parentLi.classList.add("is-active");
//         }
//     }
// }

function updateActiveLink(element) {
    console.log("update activate link");
    if (!element) return;
    
    const items = document.querySelectorAll('.dashboard-item');
    items.forEach(li => li.classList.remove("is-active"));
    
    // Get the element's ID
    let link_type = element.id || element.dataset.sidebarTarget;
    console.log("link type: ", link_type);
    
    // If it's a sidebar link, find the parent li directly
    if (element.classList.contains('sidebar_link')) {
        const parentLi = element.closest("li");
        if (parentLi) {
            parentLi.classList.add("is-active");
        }
        return;
    }
    
    // For non-sidebar elements, map ID to li selector
    const idMap = {
        // Profile related
        'profile_header': '#edit_profile_li',
        'complete_profile': '#edit_profile_li',
        'edit_profile_label': '#edit_profile_li',
        'profile_faq_en': '#edit_profile_li',
        'profile_faq_cn': '#edit_profile_li',
        // Address related
        'addresses_header': '#addresses_li',
        'addresses': '#addresses_li',
        'address_book_label': '#addresses_li',
        // Orders related
        'orders_header': '#orders_li',
        'works_owned': '#orders_li',
        // Offers related
        'offers_header': '#perks_li',
        'perks_label': '#perks_li',
        // Vouchers related
        'vouchers_header': '#vouchers_li',
        'my_vouchers': '#vouchers_li',
        // Wishlist related
        'wishlist_header': '#wishlist_li',
        'wishlist_label': '#wishlist_li',
        // Favorites related
        'favorites_header': '#favorites_li',
        'favorites_label': '#favorites_li',
        // Help related
        'help_header': '#help_li',
        'helpdesk': '#help_li',
        'help_faq_en1': '#help_li',
        'help_faq_cn1': '#help_li',
        'help_faq_en2': '#help_li',
        'help_faq_cn2': '#help_li',
        // 3D related
        'threed_header': '#threed_li',
        'threed_label': '#threed_li',
        // Main default
        'main_link': '#main_li',
    };
    
    // Handle dynamic "order_" prefix
    if (link_type && link_type.startsWith("order_")) {
        const helpLi = document.querySelector("#help_li");
        if (helpLi) helpLi.classList.add("is-active");
        return;
    }
    
    // Find the target li
    const targetSelector = idMap[link_type];
    if (targetSelector) {
        const targetLi = document.querySelector(targetSelector);
        if (targetLi) targetLi.classList.add("is-active");
    } else {
        // Default fallback
        const mainLi = document.querySelector("#main_li");
        if (mainLi) mainLi.classList.add("is-active");
    }
}

// ============================================================
// 📩 NOTIFICATION DOT CONTROLLER
// ============================================================
function updateNotificationEnvelope() {
    const envelope = document.getElementById('notification-envelope');
    if (!envelope) {
        // Element not found - try again after a delay
        setTimeout(updateNotificationEnvelope, 100);
        return;
    }
    
    // Get unread count from multiple sources for reliability
    let unreadCount = 0;
    
    // Source 1: Check the header badge
    const headerBadge = document.getElementById('unread-count-header');
    if (headerBadge) {
        const text = headerBadge.textContent.trim();
        unreadCount = parseInt(text) || 0;
    }
    
    // // Source 2: Check the sidebar badge (fallback)
    // if (unreadCount === 0) {
    //     const sidebarBadge = document.getElementById('unread-count-sidebar');
    //     if (sidebarBadge) {
    //         const text = sidebarBadge.textContent.trim();
    //         unreadCount = parseInt(text) || 0;
    //     }
    // }
    
    // // Source 3: Check the total unread badge on help page
    // if (unreadCount === 0) {
    //     const totalBadge = document.getElementById('total_unread_count_badge_member');
    //     if (totalBadge) {
    //         const text = totalBadge.textContent.trim();
    //         unreadCount = parseInt(text) || 0;
    //     }
    // }
    
    // // Show/hide envelope based on unread count
    // if (unreadCount > 0) {
    //     envelope.classList.remove('hidden');
    //     // Add a small number badge if > 1
    //     updateEnvelopeCount(unreadCount);
    // } else {
    //     envelope.classList.add('hidden');
    // }

    if (unreadCount > 0) {
        envelope.classList.remove('hidden');
    } else {
        envelope.classList.add('hidden');
    }
}

function updateEnvelopeCount(count) {
    const envelope = document.getElementById('notification-envelope');
    if (!envelope) return;
    
    // Check if we already have a count badge
    let countBadge = envelope.querySelector('.envelope-count');
    
    if (count > 1) {
        if (!countBadge) {
            // Create count badge
            countBadge = document.createElement('span');
            countBadge.className = 'envelope-count absolute -top-1 -right-1 bg-error text-white text-[8px] font-bold rounded-full w-3.5 h-3.5 flex items-center justify-center ring-2 ring-white/80';
            // Find the envelope icon container
            const iconContainer = envelope.querySelector('.bg-error');
            if (iconContainer) {
                iconContainer.appendChild(countBadge);
            }
        }
        countBadge.textContent = count > 9 ? '9+' : count;
        countBadge.classList.remove('hidden');
    } else {
        if (countBadge) {
            countBadge.classList.add('hidden');
        }
    }
}

// ✅ Update envelope when refresh_count event fires
document.body.addEventListener('refresh_count', function() {
    // Small delay to ensure badges have updated
    setTimeout(updateNotificationEnvelope, 50);
});

// ✅ Update envelope on page load
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(updateNotificationEnvelope, 500);
});

// ✅ Update envelope after HTMX swaps
document.body.addEventListener('htmx:afterSwap', function(evt) {
    const targetId = evt.detail.target?.id;
    if (targetId === 'dashboard-content' || 
        targetId === 'unread-count-header' ||
        targetId === 'unread-count-sidebar' ||
        targetId === 'total_unread_count_badge_member') {
        setTimeout(updateNotificationEnvelope, 100);
    }
});

// ✅ Also update when page becomes visible (tab switch)
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        setTimeout(updateNotificationEnvelope, 200);
    }
});

// ✅ Update on pageshow (bfcache restore)
window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        setTimeout(updateNotificationEnvelope, 300);
    }
});


window.confirmSweetAlertDelete = confirmSweetAlertDelete;
window.daysBetween = daysBetween;
window.datePicker = datePicker;
window.searchArchive = searchArchive;
window.resetDate = resetDate;
window.formatter = formatter;
window.format_currency = format_currency
window.updateHeaderCartDetails = updateHeaderCartDetails;
window.check_element_exist = check_element_exist;
window.check_elements_exist = check_elements_exist;
window.Swal = Swal
window.confirmAction = confirmAction
window.share_link = share_link
window.delete_wish = delete_wish
window.GLightbox = GLightbox
// window.change_thumbnail_image = change_thumbnail_image
window.post_and_fetch_data = post_and_fetch_data
window.htmx = htmx;

window.get_csrf_token = get_csrf_token

window.preAutoComplete = preAutoComplete;
window.initAutoComplete = initAutoComplete;
window.initRegionLogic = initRegionLogic;
window.toggleProvinceFields = toggleProvinceFields;
window.openOrderDetailsModal = openOrderDetailsModal;
window.closeOrderDetailsModal = closeOrderDetailsModal;
window.triggerOrderCancellation = triggerOrderCancellation;

window.updateActiveLink = updateActiveLink;
window.updateNotificationEnvelope = updateNotificationEnvelope;
