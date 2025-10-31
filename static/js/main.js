import "@/css/main.css"

import Swiper from 'swiper'
import { Navigation, Pagination } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import "cally"
import Swal from 'sweetalert2'

import { firework } from "./firework"


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
    // startDateDisplay.setAttribute("min", "2025-01-01");
    // console.log(startDateDisplay.min)

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
// const fireworkEl = document.querySelector(".firework_gl") ? window.onload = firework() : null

window.daysBetween = daysBetween;
window.datePicker = datePicker;
window.searchArchive = searchArchive;
window.resetDate = resetDate;
