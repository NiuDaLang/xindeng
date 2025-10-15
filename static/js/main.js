import "@/css/main.css"

import Swiper from 'swiper'
import { Navigation, Pagination } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'


// ***** change theme *****
let checkbox = document.querySelector("#day_night_checkbox")
let lightTheme = "valentine"
let darkTheme = "aqua"
let selectedTheme = localStorage.getItem("theme")
const is_dark = window.matchMedia("(prefers-color-scheme: dark)").matches;

// (1) on document load, set checkbox status + set localStorage's theme
document.addEventListener('DOMContentLoaded', function() {
    if(localStorage.getItem("theme")==="auto"){
        is_dark ? localStorage.setItem("theme", darkTheme) : localStorage.setItem("theme", lightTheme)
        return
    }
    checkbox.checked = localStorage.getItem("theme") === darkTheme ? true : false
    if(!selectedTheme){
        if(is_dark){
            localStorage.setItem("theme", darkTheme)
            checkbox.checked = true
        } else {
            localStorage.setItem("theme", lightTheme)
            checkbox.checked = false
        }
    }
    document.documentElement.setAttribute('data-theme', localStorage.getItem("theme"));
});

// (2) for default mode, enable << light <==> dark >> toggle
checkbox.addEventListener("click", () => {
    if(checkbox.checked) {
        // if dark mode
        localStorage.setItem("theme", darkTheme)
    } else {
        // if light mode
        localStorage.setItem("theme", lightTheme)
    }
    document.documentElement.setAttribute('data-theme', localStorage.getItem("theme"));
})

// ***** change navbar color on-scroll *****
window.addEventListener('scroll', function() {
    const header = document.querySelector("#navbar")
    const scrollThreshold = 100; // Change color after scrolling 100 pixels

    if (window.scrollY > scrollThreshold) {
        header.classList.add('scrolled-background');
    } else {
        header.classList.remove('scrolled-background');
    }
});    

// ***** swiper *****
const swiper = new Swiper('.swiper', {
    modules: [Navigation, Pagination],
    direction: 'horizontal',
    loop: true,
    pagination: {
        el: '.swiper-pagination',
    },
    navigation: {
        nextEl: '.swiper-btn-next',
        prevEl: '.swiper-btn-prev',
    },
    scrollbar: {
        el: '.swiper-scrollbar',
    },
});

