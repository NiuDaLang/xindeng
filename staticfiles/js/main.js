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
window.addEventListener('scroll', function() {
    // const header = document.querySelector("#navbar")
    const header = check_element_exist(this.document, "#navbar")
    if(header) {
        const scrollThreshold = 100; // Change color after scrolling 100 pixels
    
        if (window.scrollY > scrollThreshold) {
            header.classList.add('scrolled-background');
        } else {
            header.classList.remove('scrolled-background');
        }
    }
});    

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
const updateHeaderCartDetails = (items_count, items_total) => {
    document.querySelector("#cart_count_icon").innerText = items_count;
    document.querySelector("#cart_count").innerText = `${items_count} Items`
    document.querySelector("#cart_sub_total").innerText = `CNY ${items_total}`
}

// share function
const share_link = async (title, text, link) => {
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
function get_csrf_token(){
    const csrf_element = document.querySelector("[name=csrfmiddlewaretoken]");
    if (!csrf_element) {
        console.error("CSRF tokenelement not found in template!")
        return null
    }
    return csrf_element.value;
}

async function createOrder() {
    // User authentication
    const proforma_invoice_number = JSON.parse(document.getElementById('proforma_invoice_number').textContent)
    const foreign_currency_code = JSON.parse(document.getElementById('foreign_currency_code').textContent)
    const locked_rate = JSON.parse(document.getElementById('locked_rate').textContent)

    try {
        // const response = await fetch(`/orders/api/paypal/create_paypal_order/?invoice=${proforma_invoice_number}&foreign_currency_code=${foreign_currency_code}&locked_rate=${locked_rate}`, {
        //     method: "POST",
        //     headers: {
        //         "X-CSRFToken": get_csrf_token(),
        //         "Content-Type": "application/json",
        //     },
        // });
        const url = `/orders/api/paypal/create_paypal_order/?invoice=${proforma_invoice_number}&foreign_currency_code=${foreign_currency_code}&locked_rate=${locked_rate}`
        const headers = {
                "X-CSRFToken": get_csrf_token(),
                "Content-Type": "application/json",
                "mode": 'same-origin',
            }
        const body = null
        const response_data = await post_and_fetch_data(url, headers, body)
        // const data = await response.json()
        // if(!response.ok){throw new Error(errorData.error || "Failed to create order");}
        
        console.log("Returning Order ID: ", response_data.id)
        return {orderId: response_data.id}

    } catch(error) {
        console.error("Failed to create order:", error);
        throw error;
    }
}

async function captureOrder(data) {
    try {
        // const response = await fetch(
        //     `/orders/api/paypal/capture_paypal_order/?paypal_order_id=${data.orderId}`,
        //     {
        //         method: "POST",
        //         headers: {
        //             "Content-Type": "application/json",
        //             "X-CSRFToken": csrf_token,
        //             "mode": 'same-origin',
        //         },
        //         body: JSON.stringify(data),
        //     }
        // );

        const url = `/orders/api/paypal/capture_paypal_order/?paypal_order_id=${data.orderId}`
        const headers = {
                "X-CSRFToken": get_csrf_token(),
                "Content-Type": "application/json",
                "mode": 'same-origin',
            }
        const body = JSON.stringify(data)
        const response_data = await post_and_fetch_data(url, headers, body)

        // if(!response.ok){
        //     const errorData = await response.json();
        //     throw new Error(errorData.error || "Failed to capture order");
        // }

        // const res_data = await response.json()
        console.log("captured res_data: ", response_data)

        return response_data
        
    } catch (error) {
        console.error("Failed to capture order", error)
        throw error
    }
}

async function orderSuccess(data) {
    // const invoice_id = data.purchase_units[0].invoice_id // production
    const invoice_id = JSON.parse(document.getElementById('proforma_invoice_number').textContent)
    const locked_rate = JSON.parse(document.getElementById('locked_rate').textContent)
    console.log("invoice_id: ", invoice_id)
    console.log("locked_rate: ", locked_rate)

    try {
        // const response = await fetch(
        //     `/orders/api/paypal/paypal_order_success/?invoice_id=${invoice_id}`,
        //     {
        //         method: "POST",
        //         headers: {
        //             "Content-Type": "application/json",
        //             "X-CSRFToken": csrf_token,
        //             "mode": 'same-origin',
        //         },
        //         body: JSON.stringify(data),
        //     }
        // )

        const url = `/orders/api/paypal/paypal_order_success/?invoice_id=${invoice_id}&exchange_rate=${locked_rate}`
        const headers = {
                "X-CSRFToken": get_csrf_token(),
                "Content-Type": "application/json",
                "mode": 'same-origin',
            }
        const body = JSON.stringify(data)
        const response_data = await post_and_fetch_data(url, headers, body)

        // if(!response.ok){
        //     const errorData = await response.json();
        //     throw new Error(errorData.error || "Failed to process successful order");
        // }

        // const res_data = await response.json()
        console.log("order_success res_data: ", response_data)

        return response_data
        
    } catch (error) {
        console.error("Failed to record order", error)
        throw error
    }
}

// fetch token
async function getBrowserSafeClientToken() {
    const csrf_element = document.querySelector("[name=csrfmiddlewaretoken]");
    if (!csrf_element) {
        console.error("CSRF tokenelement not found in template!")
        return null
    }
    const csrf_token = csrf_element.value;
    const response = await fetch("/orders/api/paypal/token/", {
        method: "POST",
        headers: {
            "X-CSRFToken": csrf_token,
            "Content-Type": "application/json",
        },
    });
    const data = await response.json();
    console.log("data: ", data);
    return data;
}

// init function to be run if paypal container is found in the page
async function initializePayPalSDK() {
    const paypalButton = document.querySelector("paypal-button");
    const foreign_currency_code = JSON.parse(document.getElementById('foreign_currency_code').textContent)
    const country_code = JSON.parse(document.getElementById('country_code').textContent)

    try {
        // 1. Fetch the client token securely from the server
        const data = await getBrowserSafeClientToken();
        const clientToken = await data.access_token

        // 2. Load the PayPal SDK script dynamically
        // Note: In v6, you load the general script first, then initialize with the token.
        const script = document.createElement('script');
        script.src = "https://www.sandbox.paypal.com/web-sdk/v6/core"; // Use v6 specific URL (production: paypal instead of sandbox)
        script.async = true;
        
        script.onload = async () => {
            // 3. Initialize the SDK instance with the clientToken after the script loads
            try {
                const sdkInstance = await window.paypal.createInstance({
                    clientToken: clientToken,
                    components: ["paypal-payments"],
                    // pageType: "checkout",
                    // locale: "en-US",
                    // clientMetadataId: crypto.randomUUID(),
                });
                // 4. check available methods
                console.log("foreign_currency_code: ", foreign_currency_code)
                console.log("locale: ", country_code)
                const methods = await sdkInstance.findEligibleMethods({
                    currencyCode: foreign_currency_code,
                    countryCode: country_code,
                });

                // 5. if method(s) available, render PayPal button
                if (methods.isEligible("paypal")) {
                    //   show button
                    paypalButton.removeAttribute("hidden");
                }
                // 6. setup one-time payment session
                const paymentSession = sdkInstance.createPayPalOneTimePaymentSession({
                    onApprove: async (data) => {
                        console.log("Payment approved:", data);
                        try {
                            const captured_data = await captureOrder(data);
                            console.log("captured_data: ", captured_data)
                            
                            if(captured_data.status === "COMPLETED"){
                                const payment_success_data = await orderSuccess(captured_data)
                                console.log("payment_success: ", payment_success_data)
                                window.location.href = `/orders/order_complete/?order_number=${payment_success_data.order_number}&transaction_id=${payment_success_data.transaction_id}`
                            }
                        } catch (error) {
                            throw new Error("Payment capture failed:", error);
                        }
                    },

                    // Called when user cancels a payment
                    onCancel(data) {console.log("Payment cancelled:", data);},
                    
                    // Called when an error occurs during payment
                    onError(error) {console.error("Payment error:", error);},
                })
                // 7. attach click listener to button
                paypalButton.addEventListener("click", async () => {
                    await paymentSession.start({ presentationMode: "auto" }, createOrder())
                })
            } catch (createInstanceError) {
                console.error('PayPal createInstance failed:', createInstanceError);
            }
        };

        script.onerror = (error) => {console.error("Failed to load the PayPal JS SDK script", error);};

        document.body.appendChild(script);

    } catch (error) {
        console.error("Error during PayPal initialization:", error);
    }
}

// if (place_order_pattern.test(window.location.href)) {
const paypal_btns = check_element_exist(document, "#paypal_btns")
if (paypal_btns) {
    initializePayPalSDK()
}



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
window.share_link = share_link
window.delete_wish = delete_wish
window.GLightbox = GLightbox
window.change_thumbnail_image = change_thumbnail_image
window.post_and_fetch_data = post_and_fetch_data


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


