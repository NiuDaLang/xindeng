import "@/css/main.css"

import Swiper from 'swiper'
import { Navigation, Pagination } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
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

// 1. Maintain a clean backup reference to the browser's native error engine
const originalConsoleError = console.error;

// 2. Listen for the native popstate event (fires the instant a user hits the back button)
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

// ***** change theme *****
// let checkbox = document.querySelector("#day_night_checkbox")
// let lightTheme = "valentine"
// let darkTheme = "aqua"
// let selectedTheme = localStorage.getItem("theme")
// const is_dark = window.matchMedia("(prefers-color-scheme: dark)").matches;

// // (1) on document load, set checkbox status + set localStorage's theme
// document.addEventListener('DOMContentLoaded', function() {
//     if(localStorage.getItem("theme")==="auto"){
//         is_dark ? localStorage.setItem("theme", darkTheme) : localStorage.setItem("theme", lightTheme)
//         return
//     }
//     checkbox.checked = localStorage.getItem("theme") === darkTheme ? true : false
//     if(!selectedTheme){
//         if(is_dark){
//             localStorage.setItem("theme", darkTheme)
//             checkbox.checked = true
//         } else {
//             localStorage.setItem("theme", lightTheme)
//             checkbox.checked = false
//         }
//     }
//     document.documentElement.setAttribute('data-theme', localStorage.getItem("theme"));
// });

// (2) for default mode, enable << light <==> dark >> toggle
// checkbox.addEventListener("click", () => {
//     if(checkbox.checked) {
//         // if dark mode
//         localStorage.setItem("theme", darkTheme)
//     } else {
//         // if light mode
//         localStorage.setItem("theme", lightTheme)
//     }
//     document.documentElement.setAttribute('data-theme', localStorage.getItem("theme"));
// })

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

// ***** swiper *****
// const swiper = new Swiper('.swiper', {
//     modules: [Navigation, Pagination],
//     direction: 'horizontal',
//     loop: true,
//     pagination: {
//         el: '.swiper-pagination',
//     },
//     navigation: {
//         nextEl: '.swiper-btn-next',
//         prevEl: '.swiper-btn-prev',
//     },
//     scrollbar: {
//         el: '.swiper-scrollbar',
//     },
// });

// ***** glightbox (product - gallery) *****
let dynamicLightbox; // gallery
let base_data = []
let slides_data = [];
let product_gallery_images = {};
let variations_gallery_data = []

// Init Glightbox
function init_glightbox (slides_data) {
    const main_contents = [...document.querySelectorAll(".glight_main")]
    dynamicLightbox = GLightbox({
        elements: slides_data,
        onclose: () => { dynamicLightbox.destroy(); }
    });
    // Solve the "hidden-aria" issue
    dynamicLightbox.on('open', () => {
        if (main_contents) {
            main_contents.map(main_content => {
                main_content.setAttribute("inert", "")
                main_content.setAttribute("aria-hidden", "false")
            })
        }
    });
    dynamicLightbox.on('close', () => {
        if (main_contents) {
            main_contents.map(main_content => {
                main_content.removeAttribute('inert');
            })
        }
    });    
}

// function to move picture data within the list
function moveItem(array, fromIndex, toIndex) {
    const [item] = array.splice(fromIndex, 1);
    array.splice(toIndex, 0, item);
    return array;
}

// function to reorder the gallery
function reorder_image_to_gallery_head (index) {
    if (base_data.length > 1) {
        slides_data = moveItem([...base_data], index, 0);
        init_glightbox(slides_data)
    } else {
        console.log("Cannot reorder gallery (requires initialization or >1 image).");
    }
}

// Change thumbnail image upon clicking small gallery image
function change_thumbnail_image(e, gallery_images_object, target_el){
    const image_key = e.target.id
    if(gallery_images_object[image_key]){
        target_el.src = gallery_images_object[image_key]
    } else {
        console.error("Image key not found:", image_key);
    }
}

// Initial method for 1st gallery DOM
function init_gallery_top_dom (product_gallery_images, target_el, e){
    slides_data = [...base_data]
    init_glightbox(slides_data)
    change_thumbnail_image(e, product_gallery_images, target_el)
    dynamicLightbox.reload();
}

// Initial method for other gallery DOMs
function init_gallery_other_doms (product_gallery_images, target_el, pic_index, e) {
    change_thumbnail_image(e, product_gallery_images, target_el)
    reorder_image_to_gallery_head(pic_index)
    dynamicLightbox.reload();
}

document.addEventListener("DOMContentLoaded", function(event){
    // parse backend product-gallery data
    const product_gallery_script_tag = document.getElementById('product_gallery_json_data');
    const variations_gallery_script_tag = document.getElementById('variations_gallery_json_data');

    if (product_gallery_script_tag && product_gallery_script_tag.textContent) {
        try {
            // Extract the raw text and parse it
            base_data = JSON.parse(product_gallery_script_tag.textContent);
            slides_data = [...base_data]
        } catch (e) {
            console.error("Error parsing JSON data:", e);
        }
    }

    if (variations_gallery_script_tag && variations_gallery_script_tag.textContent){
        try {
            variations_gallery_data = JSON.parse(variations_gallery_script_tag.textContent);
        } catch (e) {
            console.error("Error parsing variation JSON data:", e);
        }
    }

    function allocate_variation_gallery(main_thumbnail, variation_id, variation){
        variations_gallery_data.map(variation_gallery => {
            if(variation_gallery[0].id === variation_id){
                base_data = [{href: variation[0][1].image, title: variation[0][1].sku}, ...variation_gallery[1]]
                // (0) init gallery
                init_glightbox(base_data)
                // (1) change Thumbnail image to ProductVariation model's image
                main_thumbnail.src = variation[0][1].image
                // (2) change gallery's 1st image to ProductVariation model's image
                const main_product_image_el = check_element_exist(document, "#product_gallery_image_0")
                main_product_image_el.src = variation[0][1].image
                // (3) mark the first gallery image selected
                const main_product_image_input_el = check_element_exist(document, "#main_product_image_input")
                main_product_image_input_el.checked = true
                // (4) delete all other gallery images 
                const other_product_gallery_images = check_elements_exist(document, '.product_gallery_image_wrapper')
                if(other_product_gallery_images){
                    [...other_product_gallery_images].map(el => {el.remove()})
                }
                // (5) create new gallery images and display them
                const gallery_wrapper_el = document.querySelector("#product_gallery_images")
                if(variation_gallery[1].length > 0){
                    variation_gallery[1].map((image, index) => {
                        const gallery_img_html = `
                            <label class="switch product_gallery_image_wrapper" name="pattern">
                                <input type="radio" name="pattern">
                                <img id="product_gallery_image_${index+1}" src="${image.href}" alt="${image.title}" class="switch-img rounded-sm product_gallery_image"></img>
                            </label>
                        `                        
                        gallery_wrapper_el.insertAdjacentHTML("beforeend", gallery_img_html)
                    })
                }
                // (6) cancel the current addEventListener method registered on the first gallery image from initialization
                main_product_image_el.removeEventListener("click", window.gallery_top_dom_handler)
                // (7) register new addEventListener method
                product_gallery_images = {}
                // (7-a) top image of the gallery
                product_gallery_images[main_product_image_el.id] = main_product_image_el.src
                const gallery_top_dom_handler = init_gallery_top_dom.bind(null, product_gallery_images, main_thumbnail)
                main_product_image_el.addEventListener("click", gallery_top_dom_handler)
                window.gallery_top_dom_handler = gallery_top_dom_handler
                // (7-b) other gallery images
                const product_gallery_image_els = check_elements_exist(document, ".product_gallery_image")
                if(product_gallery_image_els) {
                    product_gallery_image_els.map(el => {
                        const pic_index = Number(el.id.replace("product_gallery_image_", ""))
                        product_gallery_images[el.id] = el.src

                        // When any of the gallery image is clicked
                        const gallery_other_doms_handler = init_gallery_other_doms.bind(null, product_gallery_images, main_thumbnail, pic_index)
                        el.addEventListener("click", gallery_other_doms_handler)
                    })
                }
            }
        })
    }
    
    window.allocate_variation_gallery = allocate_variation_gallery
    
    // connect it with the DOM element and create GLightbox instance 
    const galleryLink = document.getElementById('open-product-gallery'); // <a> thumbnail DOM
    if (galleryLink && slides_data.length > 0) {
        init_glightbox(slides_data)

        // when thumbnail (large) image is clicked, create the GLightbox
        galleryLink.addEventListener('click', function(e) {
            e.preventDefault(); 
            dynamicLightbox.open();
        });

        // Product Gallery - if gallery image is clicked, show it to the MAIN/LARGE image box
        const target_el = document.querySelector("#main_thumbnail")

        // (a) 1st gallery image
        const main_product_gallery_image_el = check_element_exist(document, "#product_gallery_image_0")
        product_gallery_images[main_product_gallery_image_el.id] = main_product_gallery_image_el.src
        const gallery_top_dom_handler = init_gallery_top_dom.bind(null, product_gallery_images, target_el)
        main_product_gallery_image_el.addEventListener("click", gallery_top_dom_handler)
        window.gallery_top_dom_handler = gallery_top_dom_handler

        // (b) other gallery images
        const product_gallery_image_els = check_elements_exist(document, ".product_gallery_image")
        if(product_gallery_image_els) {
            product_gallery_image_els.map(el => {
                const pic_index = Number(el.id.replace("product_gallery_image_", ""))
                product_gallery_images[el.id] = el.src

                // When any of the gallery image is clicked
                const gallery_other_doms_handler = init_gallery_other_doms.bind(null, product_gallery_images, target_el, pic_index)
                el.addEventListener("click", gallery_other_doms_handler)
            })
        }
    }
})


// ***** Sharer.js *****
document.addEventListener('DOMContentLoaded', () => {
    if (window.Sharer) {
            window.Sharer.init();
        } else {
            console.error("window.Sharer is not defined. Check installation.");
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
function check_element_exist(parent, selector) {
    const element = parent.querySelector(selector);
    if (element) {
        return element
    } else {
        // This runs if the element was not found
        return false
    }
}

function check_elements_exist(parent, selector) {
    const elements = parent.querySelectorAll(selector);
    if (elements) {
        return [...elements]
    } else {
        // This runs if the element was not found
        return false
    }
}

// 3D Fireworks
window.onload = function() { 
    const threeEl = document.querySelector(".webgl")
    const fireworkEl = document.querySelector(".firework_gl")
    fireworkEl ? (firework(),         
        Swal.fire({
            title: "點擊場景點燃🎆",
            text: "🖱️左鍵拖拽可觀看3D景色",
            icon: "info"
        })
) : null
}

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

            <li class="flex hover:bg-base-200 transition-colors duration-300 ease-in-out rounded-2xl items-center mt-2">
                <a href="${item.url}" class="flex flex-col flex-grow-0 items-start p-2">
                    <span class="text-sm"><strong>${item.product}</strong></span>
                    <span class="text-[0.65rem]">${item.product_variation}</span>
                    <img src="${item.image_url}" alt="product image" class="rounded-e-4xl">
                </a>
                <div class="h-full flex gap-1 items-center mr-2">
                    <span class="">X</span>
                    <span id="header_item_qty_${item.id}" class="flex-grow-1">${item.quantity }</span>
                </div>
            </li>

        `).join('')
    console.log("[updateHeaderCartDetails] cart_items: ", cart_items)

    const cart_items_list = document.querySelector("#cart_items_list")
    cart_items_list.innerHTML = product_list_item_html
}

// share function
const share_link = async (title, text, link) => {
    console.log("title: ", title)
    console.log("text: ", text)
    console.log("link: ", link)
    // 1. Define the data we want to share
    const shareData = {
        title: title,
        text: text,
        url: link,
    };

    // 2. Check if the Web Share API is supported (mobile devices, some desktops)
    if (navigator.share) {
        try {
            // Use the native system share dialogue
            await navigator.share(shareData);
        } catch (err) {
            console.error('Error sharing:', err);
        }
    } else {
        // 3. Fallback for desktop browsers: Use a custom pop-up menu
        // We'll simulate a simple modal or use window.open for specific links
        showCustomSharePopup(shareData);
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

function get_csrf_token(){
    const csrf_element = document.querySelector("[name=csrfmiddlewaretoken]");
    if (!csrf_element) {
        console.error("CSRF token element not found in template!");
        return null;
    }
    return csrf_element.value;
}

// async function createOrder() {
//     const proforma_invoice_number = JSON.parse(document.getElementById('proforma_invoice_number').textContent);
//     const foreign_currency_code = JSON.parse(document.getElementById('foreign_currency_code').textContent);
//     const locked_rate = JSON.parse(document.getElementById('locked_rate').textContent);

//     try {
//         const url = `/orders/api/paypal/create_paypal_order/?invoice=${proforma_invoice_number}&foreign_currency_code=${foreign_currency_code}&locked_rate=${locked_rate}`;
//         const response = await fetch(url, {
//             method: "POST",
//             headers: {
//                 "X-CSRFToken": get_csrf_token(),
//                 "Content-Type": "application/json",
//                 "mode": 'same-origin',
//             }
//         });
//         if (!response.ok) {
//             const error_data = await response.json();
//             if (error_data.error_code === "OUT_OF_STOCK") {
//                 // Dispatch native custom event to your working errorMssg listener instantly
//                 const evt = new CustomEvent("errorMssg", {
//                     detail: {
//                         title: error_data.title,
//                         text: error_data.text,
//                         redirect_url: error_data.redirect_url
//                     }
//                 });
//                 document.dispatchEvent(evt);
                
//                 // Return an empty promise rejection to stop the PayPal SDK loop cleanly
//                 return Promise.reject(new Error("Stock allocation threshold reached."));
//             }
//             throw new Error("Failed to create order due to gateway issues.");
//         }

//         const response_data = await response.json();
//         console.log("Returning PayPal Order ID: ", response_data.id);
//         return { orderId: response_data.id };
//     } catch(error) {
//         console.error("Failed to create order:", error);
//         throw error;
//     }
// }

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
                    title: 'Validation Error ｜ 驗證失敗',
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
    
    const response = await fetch("/orders/api/paypal/token/", {
        method: "POST",
        headers: {
            "X-CSRFToken": csrf_token,
            "Content-Type": "application/json",
        },
    });
    return await response.json();
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
                    title: 'Processing Payment... ｜ 正在處理支付',
                    text: 'Please do not close this window. ｜ 請勿關閉此頁面。',
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
                            title: 'Order Sync Failed ｜ 訂單同步失敗',
                            text: 'Database validation failed. Please check your network or contact support.',
                            confirmButtonText: 'OK ｜ 確定',
                            confirmButtonColor: '#3085d6'
                        });
                    }
                } catch (error) {
                    console.error("Payment capture execution exception:", error);
                    // 🎯 SWAL Fallback for pipeline capture connection exception
                    Swal.fire({
                        icon: 'error',
                        title: 'Capture Error ｜ 捕獲交易失敗',
                        text: 'Unable to communicate with payment settlement gateway.',
                        confirmButtonText: 'Retry ｜ 重試',
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
                    confirmButtonText: 'Try Alternative Method ｜ 更換支付方式',
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
                    title: 'Rates Lapsed ｜ 匯率過期',
                    text: 'Transaction halted. Please refresh to fetch current market parameters.',
                    confirmButtonText: 'Refresh ｜ 刷新頁面',
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
//             confirmButtonText: '返回購物車 ｜ Return to Cart',
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
    const { PlaceAutocompleteElement } = await google.maps.importLibrary("places");
    const { Place } = await google.maps.importLibrary("routes"); 

    const form = document.getElementById(form_id);
    if (!form) return;
            
    // 1. Find the target input (whether it's the original Django one or the Web Component)
    // Using [id$="..."] helps if Django prefixes IDs (common in FormSets)
    const oldInput = form.querySelector('[id$="id_address_line_1"]');
    if (!oldInput || oldInput.tagName === 'GMP-PLACE-AUTOCOMPLETE') return;

    // 2. Create and configure the New Web Component
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
    });

    // Sync attributes so Django POST/HTMX works
    autocomplete.id = oldInput.id;
    autocomplete.name = "address_line_1";
    autocomplete.className = oldInput.className; 
    autocomplete.placeholder = oldInput.placeholder || "Input Address...｜輸入地址..."; 
    autocomplete.style.colorScheme = 'light';

    // 3. Swap the elements
    oldInput.replaceWith(autocomplete);

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
        hiddenAddressInput.value = val;

        // IF USER MANUALLY CHANGES TEXT, THEY ARE NO LONGER VERIFIED
        const verifiedInput = form.querySelector('[id$="id_is_verified_by_google"]');
        if (verifiedInput) verifiedInput.value = "False";

        if (!val) {
            // Clear Google data if input is wiped
            ['id_google_place_id', 'id_latitude', 'id_longitude'].forEach(suffix => {
                const el = form.querySelector(`[id$="${suffix}"]`);
                if (el) el.value = '';
            });
            
            const wrapper = autocomplete.closest('label');
            wrapper?.classList.remove('border-error');
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
console.log("ignoreOobSwapErrors: ",  htmx.config.ignoreOobSwapErrors)

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
window.change_thumbnail_image = change_thumbnail_image
window.post_and_fetch_data = post_and_fetch_data
window.htmx = htmx;

window.preAutoComplete = preAutoComplete;
window.initAutoComplete = initAutoComplete;
window.initRegionLogic = initRegionLogic;
window.toggleProvinceFields = toggleProvinceFields;

// The SdkInitError: .start() expects a Promise. Received 'string' occurs 
// because you are await-ing the createOrder() function before passing it to the PayPal session.
// In the 2026 PayPal v6 SDK, paypalPaymentSession.start() requires a Promise reference 
// so it can trigger the order creation inside the secure popup it just opened. 
// By using await, you resolved the promise to a string (the ID) too early.

// 1. Fix the setUpPayPalButton Logic
// Remove the await from createOrder() and pass the promise directly.

// paypalButton.addEventListener("click", async () => {
//     // REMOVE 'await' here. You want the Promise object, not the ID string.
//     const createOrderPromiseReference = createOrder(); 
    
//     console.log("Passing Promise to PayPal...");

//     const presentationModesToTry = ["payment-handler", "popup", "modal"];

//     for (const presentationMode of presentationModesToTry) {
//       try {
//         await paypalPaymentSession.start(
//           { presentationMode },
//           createOrderPromiseReference, // PayPal will await this internally
//         );
//         break;
//       } catch (error) {
//         if (error.isRecoverable) continue;
//         throw error;
//       }
//     }
// });

// 2. Fix the createOrder Error Handling
// Your createOrder function currently returns error in the catch block. 
// This causes the promise to resolve with an error object rather than rejecting. 
// This will confuse the PayPal SDK.
// Update your createOrder catch block:

// async function createOrder() {
//     // ... existing logic ...
//     try {
//         const response = await fetch(...);
//         // ... existing response.ok check ...
//         const data = await response.json();
//         return data.id; 
//     } catch(error) {
//         console.error("Failed to create order:", error);
//         // CRITICAL: Use 'throw' so the promise is 'rejected'
//         throw error; 
//     }
// }

// 3. Check paymentSessionOptions (OnApprove)
// In your onApprove function, you are using data.id. Depending on the exact v6 sub-version, the property name might be orderID or data.orderID.
// If captureOrder fails after you fix the initialization, check the data object:

// async onApprove(data) {
//     console.log("Approval Data:", data);
//     // Ensure you are passing the correct field (usually orderID or id)
//     const orderData = await captureOrder({
//         orderId: data.orderID || data.id, 
//     });
// }

// Summary of the v6 Requirement:
// The start() method is designed to prevent popup blockers. It needs the Promise so it can immediately open the window and then populate it with the Order ID once your server responds. By resolving it yourself first, you broke the "intent" chain required by the SDK.