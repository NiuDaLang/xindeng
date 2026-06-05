function Md(n){return n!==null&&typeof n=="object"&&"constructor"in n&&n.constructor===Object}function gu(n={},e={}){const t=["__proto__","constructor","prototype"];Object.keys(e).filter(i=>t.indexOf(i)<0).forEach(i=>{typeof n[i]>"u"?n[i]=e[i]:Md(e[i])&&Md(n[i])&&Object.keys(e[i]).length>0&&gu(n[i],e[i])})}const mf={body:{},addEventListener(){},removeEventListener(){},activeElement:{blur(){},nodeName:""},querySelector(){return null},querySelectorAll(){return[]},getElementById(){return null},createEvent(){return{initEvent(){}}},createElement(){return{children:[],childNodes:[],style:{},setAttribute(){},getElementsByTagName(){return[]}}},createElementNS(){return{}},importNode(){return null},location:{hash:"",host:"",hostname:"",href:"",origin:"",pathname:"",protocol:"",search:""}};function yr(){const n=typeof document<"u"?document:{};return gu(n,mf),n}const Sg={document:mf,navigator:{userAgent:""},location:{hash:"",host:"",hostname:"",href:"",origin:"",pathname:"",protocol:"",search:""},history:{replaceState(){},pushState(){},go(){},back(){}},CustomEvent:function(){return this},addEventListener(){},removeEventListener(){},getComputedStyle(){return{getPropertyValue(){return""}}},Image(){},Date(){},screen:{},setTimeout(){},clearTimeout(){},matchMedia(){return{}},requestAnimationFrame(n){return typeof setTimeout>"u"?(n(),null):setTimeout(n,0)},cancelAnimationFrame(n){typeof setTimeout>"u"||clearTimeout(n)}};function Kt(){const n=typeof window<"u"?window:{};return gu(n,Sg),n}function Eg(n=""){return n.trim().split(" ").filter(e=>!!e.trim())}function Mg(n){const e=n;Object.keys(e).forEach(t=>{try{e[t]=null}catch{}try{delete e[t]}catch{}})}function gf(n,e=0){return setTimeout(n,e)}function aa(){return Date.now()}function Tg(n){const e=Kt();let t;return e.getComputedStyle&&(t=e.getComputedStyle(n,null)),!t&&n.currentStyle&&(t=n.currentStyle),t||(t=n.style),t}function Ag(n,e="x"){const t=Kt();let i,r,s;const o=Tg(n);return t.WebKitCSSMatrix?(r=o.transform||o.webkitTransform,r.split(",").length>6&&(r=r.split(", ").map(a=>a.replace(",",".")).join(", ")),s=new t.WebKitCSSMatrix(r==="none"?"":r)):(s=o.MozTransform||o.OTransform||o.MsTransform||o.msTransform||o.transform||o.getPropertyValue("transform").replace("translate(","matrix(1, 0, 0, 1,"),i=s.toString().split(",")),e==="x"&&(t.WebKitCSSMatrix?r=s.m41:i.length===16?r=parseFloat(i[12]):r=parseFloat(i[4])),e==="y"&&(t.WebKitCSSMatrix?r=s.m42:i.length===16?r=parseFloat(i[13]):r=parseFloat(i[5])),r||0}function bo(n){return typeof n=="object"&&n!==null&&n.constructor&&Object.prototype.toString.call(n).slice(8,-1)==="Object"}function Cg(n){return typeof window<"u"&&typeof window.HTMLElement<"u"?n instanceof HTMLElement:n&&(n.nodeType===1||n.nodeType===11)}function hn(...n){const e=Object(n[0]),t=["__proto__","constructor","prototype"];for(let i=1;i<n.length;i+=1){const r=n[i];if(r!=null&&!Cg(r)){const s=Object.keys(Object(r)).filter(o=>t.indexOf(o)<0);for(let o=0,a=s.length;o<a;o+=1){const l=s[o],c=Object.getOwnPropertyDescriptor(r,l);c!==void 0&&c.enumerable&&(bo(e[l])&&bo(r[l])?r[l].__swiper__?e[l]=r[l]:hn(e[l],r[l]):!bo(e[l])&&bo(r[l])?(e[l]={},r[l].__swiper__?e[l]=r[l]:hn(e[l],r[l])):e[l]=r[l])}}}return e}function So(n,e,t){n.style.setProperty(e,t)}function _f({swiper:n,targetPosition:e,side:t}){const i=Kt(),r=-n.translate;let s=null,o;const a=n.params.speed;n.wrapperEl.style.scrollSnapType="none",i.cancelAnimationFrame(n.cssModeFrameID);const l=e>r?"next":"prev",c=(d,p)=>l==="next"&&d>=p||l==="prev"&&d<=p,u=()=>{o=new Date().getTime(),s===null&&(s=o);const d=Math.max(Math.min((o-s)/a,1),0),p=.5-Math.cos(d*Math.PI)/2;let f=r+p*(e-r);if(c(f,e)&&(f=e),n.wrapperEl.scrollTo({[t]:f}),c(f,e)){n.wrapperEl.style.overflow="hidden",n.wrapperEl.style.scrollSnapType="",setTimeout(()=>{n.wrapperEl.style.overflow="",n.wrapperEl.scrollTo({[t]:f})}),i.cancelAnimationFrame(n.cssModeFrameID);return}n.cssModeFrameID=i.requestAnimationFrame(u)};u()}function $n(n,e=""){const t=Kt(),i=[...n.children];return t.HTMLSlotElement&&n instanceof HTMLSlotElement&&i.push(...n.assignedElements()),e?i.filter(r=>r.matches(e)):i}function Pg(n,e){const t=[e];for(;t.length>0;){const i=t.shift();if(n===i)return!0;t.push(...i.children,...i.shadowRoot?i.shadowRoot.children:[],...i.assignedElements?i.assignedElements():[])}}function Rg(n,e){const t=Kt();let i=e.contains(n);return!i&&t.HTMLSlotElement&&e instanceof HTMLSlotElement&&(i=[...e.assignedElements()].includes(n),i||(i=Pg(n,e))),i}function la(n){try{console.warn(n);return}catch{}}function ca(n,e=[]){const t=document.createElement(n);return t.classList.add(...Array.isArray(e)?e:Eg(e)),t}function Dg(n,e){const t=[];for(;n.previousElementSibling;){const i=n.previousElementSibling;e?i.matches(e)&&t.push(i):t.push(i),n=i}return t}function Lg(n,e){const t=[];for(;n.nextElementSibling;){const i=n.nextElementSibling;e?i.matches(e)&&t.push(i):t.push(i),n=i}return t}function Ri(n,e){return Kt().getComputedStyle(n,null).getPropertyValue(e)}function ua(n){let e=n,t;if(e){for(t=0;(e=e.previousSibling)!==null;)e.nodeType===1&&(t+=1);return t}}function vf(n,e){const t=[];let i=n.parentElement;for(;i;)e?i.matches(e)&&t.push(i):t.push(i),i=i.parentElement;return t}function Zl(n,e,t){const i=Kt();return n[e==="width"?"offsetWidth":"offsetHeight"]+parseFloat(i.getComputedStyle(n,null).getPropertyValue(e==="width"?"margin-right":"margin-top"))+parseFloat(i.getComputedStyle(n,null).getPropertyValue(e==="width"?"margin-left":"margin-bottom"))}function It(n){return(Array.isArray(n)?n:[n]).filter(e=>!!e)}function Jl(n,e=""){typeof trustedTypes<"u"?n.innerHTML=trustedTypes.createPolicy("html",{createHTML:t=>t}).createHTML(e):n.innerHTML=e}let ja;function Ig(){const n=Kt(),e=yr();return{smoothScroll:e.documentElement&&e.documentElement.style&&"scrollBehavior"in e.documentElement.style,touch:!!("ontouchstart"in n||n.DocumentTouch&&e instanceof n.DocumentTouch)}}function xf(){return ja||(ja=Ig()),ja}let Ka;function Ug({userAgent:n}={}){const e=xf(),t=Kt(),i=t.navigator.platform,r=n||t.navigator.userAgent,s={ios:!1,android:!1},o=t.screen.width,a=t.screen.height,l=r.match(/(Android);?[\s\/]+([\d.]+)?/);let c=r.match(/(iPad)(?!\1).*OS\s([\d_]+)/);const u=r.match(/(iPod)(.*OS\s([\d_]+))?/),d=!c&&r.match(/(iPhone\sOS|iOS)\s([\d_]+)/),p=i==="Win32";let f=i==="MacIntel";const _=["1024x1366","1366x1024","834x1194","1194x834","834x1112","1112x834","768x1024","1024x768","820x1180","1180x820","810x1080","1080x810"];return!c&&f&&e.touch&&_.indexOf(`${o}x${a}`)>=0&&(c=r.match(/(Version)\/([\d.]+)/),c||(c=[0,1,"13_0_0"]),f=!1),l&&!p&&(s.os="android",s.android=!0),(c||d||u)&&(s.os="ios",s.ios=!0),s}function wf(n={}){return Ka||(Ka=Ug(n)),Ka}let Za;function Og(){const n=Kt(),e=wf();let t=!1;function i(){const a=n.navigator.userAgent.toLowerCase();return a.indexOf("safari")>=0&&a.indexOf("chrome")<0&&a.indexOf("android")<0}if(i()){const a=String(n.navigator.userAgent);if(a.includes("Version/")){const[l,c]=a.split("Version/")[1].split(" ")[0].split(".").map(u=>Number(u));t=l<16||l===16&&c<2}}const r=/(iPhone|iPod|iPad).*AppleWebKit(?!.*Safari)/i.test(n.navigator.userAgent),s=i(),o=s||r&&e.ios;return{isSafari:t||s,needPerspectiveFix:t,need3dFix:o,isWebView:r}}function yf(){return Za||(Za=Og()),Za}function Fg({swiper:n,on:e,emit:t}){const i=Kt();let r=null,s=null;const o=()=>{!n||n.destroyed||!n.initialized||(t("beforeResize"),t("resize"))},a=()=>{!n||n.destroyed||!n.initialized||(r=new ResizeObserver(u=>{s=i.requestAnimationFrame(()=>{const{width:d,height:p}=n;let f=d,_=p;u.forEach(({contentBoxSize:g,contentRect:m,target:h})=>{h&&h!==n.el||(f=m?m.width:(g[0]||g).inlineSize,_=m?m.height:(g[0]||g).blockSize)}),(f!==d||_!==p)&&o()})}),r.observe(n.el))},l=()=>{s&&i.cancelAnimationFrame(s),r&&r.unobserve&&n.el&&(r.unobserve(n.el),r=null)},c=()=>{!n||n.destroyed||!n.initialized||t("orientationchange")};e("init",()=>{if(n.params.resizeObserver&&typeof i.ResizeObserver<"u"){a();return}i.addEventListener("resize",o),i.addEventListener("orientationchange",c)}),e("destroy",()=>{l(),i.removeEventListener("resize",o),i.removeEventListener("orientationchange",c)})}function Ng({swiper:n,extendParams:e,on:t,emit:i}){const r=[],s=Kt(),o=(c,u={})=>{const d=s.MutationObserver||s.WebkitMutationObserver,p=new d(f=>{if(n.__preventObserver__)return;if(f.length===1){i("observerUpdate",f[0]);return}const _=function(){i("observerUpdate",f[0])};s.requestAnimationFrame?s.requestAnimationFrame(_):s.setTimeout(_,0)});p.observe(c,{attributes:typeof u.attributes>"u"?!0:u.attributes,childList:n.isElement||(typeof u.childList>"u"?!0:u).childList,characterData:typeof u.characterData>"u"?!0:u.characterData}),r.push(p)},a=()=>{if(n.params.observer){if(n.params.observeParents){const c=vf(n.hostEl);for(let u=0;u<c.length;u+=1)o(c[u])}o(n.hostEl,{childList:n.params.observeSlideChildren}),o(n.wrapperEl,{attributes:!1})}},l=()=>{r.forEach(c=>{c.disconnect()}),r.splice(0,r.length)};e({observer:!1,observeParents:!1,observeSlideChildren:!1}),t("init",a),t("destroy",l)}var kg={on(n,e,t){const i=this;if(!i.eventsListeners||i.destroyed||typeof e!="function")return i;const r=t?"unshift":"push";return n.split(" ").forEach(s=>{i.eventsListeners[s]||(i.eventsListeners[s]=[]),i.eventsListeners[s][r](e)}),i},once(n,e,t){const i=this;if(!i.eventsListeners||i.destroyed||typeof e!="function")return i;function r(...s){i.off(n,r),r.__emitterProxy&&delete r.__emitterProxy,e.apply(i,s)}return r.__emitterProxy=e,i.on(n,r,t)},onAny(n,e){const t=this;if(!t.eventsListeners||t.destroyed||typeof n!="function")return t;const i=e?"unshift":"push";return t.eventsAnyListeners.indexOf(n)<0&&t.eventsAnyListeners[i](n),t},offAny(n){const e=this;if(!e.eventsListeners||e.destroyed||!e.eventsAnyListeners)return e;const t=e.eventsAnyListeners.indexOf(n);return t>=0&&e.eventsAnyListeners.splice(t,1),e},off(n,e){const t=this;return!t.eventsListeners||t.destroyed||!t.eventsListeners||n.split(" ").forEach(i=>{typeof e>"u"?t.eventsListeners[i]=[]:t.eventsListeners[i]&&t.eventsListeners[i].forEach((r,s)=>{(r===e||r.__emitterProxy&&r.__emitterProxy===e)&&t.eventsListeners[i].splice(s,1)})}),t},emit(...n){const e=this;if(!e.eventsListeners||e.destroyed||!e.eventsListeners)return e;let t,i,r;return typeof n[0]=="string"||Array.isArray(n[0])?(t=n[0],i=n.slice(1,n.length),r=e):(t=n[0].events,i=n[0].data,r=n[0].context||e),i.unshift(r),(Array.isArray(t)?t:t.split(" ")).forEach(o=>{e.eventsAnyListeners&&e.eventsAnyListeners.length&&e.eventsAnyListeners.forEach(a=>{a.apply(r,[o,...i])}),e.eventsListeners&&e.eventsListeners[o]&&e.eventsListeners[o].forEach(a=>{a.apply(r,i)})}),e}};function Bg(){const n=this;let e,t;const i=n.el;typeof n.params.width<"u"&&n.params.width!==null?e=n.params.width:e=i.clientWidth,typeof n.params.height<"u"&&n.params.height!==null?t=n.params.height:t=i.clientHeight,!(e===0&&n.isHorizontal()||t===0&&n.isVertical())&&(e=e-parseInt(Ri(i,"padding-left")||0,10)-parseInt(Ri(i,"padding-right")||0,10),t=t-parseInt(Ri(i,"padding-top")||0,10)-parseInt(Ri(i,"padding-bottom")||0,10),Number.isNaN(e)&&(e=0),Number.isNaN(t)&&(t=0),Object.assign(n,{width:e,height:t,size:n.isHorizontal()?e:t}))}function zg(){const n=this;function e(y,P){return parseFloat(y.getPropertyValue(n.getDirectionLabel(P))||0)}const t=n.params,{wrapperEl:i,slidesEl:r,rtlTranslate:s,wrongRTL:o}=n,a=n.virtual&&t.virtual.enabled,l=a?n.virtual.slides.length:n.slides.length,c=$n(r,`.${n.params.slideClass}, swiper-slide`),u=a?n.virtual.slides.length:c.length;let d=[];const p=[],f=[];let _=t.slidesOffsetBefore;typeof _=="function"&&(_=t.slidesOffsetBefore.call(n));let g=t.slidesOffsetAfter;typeof g=="function"&&(g=t.slidesOffsetAfter.call(n));const m=n.snapGrid.length,h=n.slidesGrid.length,v=n.size-_-g;let x=t.spaceBetween,w=-_,S=0,C=0;if(typeof v>"u")return;typeof x=="string"&&x.indexOf("%")>=0?x=parseFloat(x.replace("%",""))/100*v:typeof x=="string"&&(x=parseFloat(x)),n.virtualSize=-x-_-g,c.forEach(y=>{s?y.style.marginLeft="":y.style.marginRight="",y.style.marginBottom="",y.style.marginTop=""}),t.centeredSlides&&t.cssMode&&(So(i,"--swiper-centered-offset-before",""),So(i,"--swiper-centered-offset-after",""));const T=t.grid&&t.grid.rows>1&&n.grid;T?n.grid.initSlides(c):n.grid&&n.grid.unsetSlides();let A;const b=t.slidesPerView==="auto"&&t.breakpoints&&Object.keys(t.breakpoints).filter(y=>typeof t.breakpoints[y].slidesPerView<"u").length>0;for(let y=0;y<u;y+=1){A=0;const P=c[y];if(!(P&&(T&&n.grid.updateSlide(y,P,c),Ri(P,"display")==="none"))){if(a&&t.slidesPerView==="auto")t.virtual.slidesPerViewAutoSlideSize&&(A=t.virtual.slidesPerViewAutoSlideSize),A&&P&&(t.roundLengths&&(A=Math.floor(A)),P.style[n.getDirectionLabel("width")]=`${A}px`);else if(t.slidesPerView==="auto"){b&&(P.style[n.getDirectionLabel("width")]="");const D=getComputedStyle(P),O=P.style.transform,V=P.style.webkitTransform;if(O&&(P.style.transform="none"),V&&(P.style.webkitTransform="none"),t.roundLengths)A=n.isHorizontal()?Zl(P,"width"):Zl(P,"height");else{const k=e(D,"width"),G=e(D,"padding-left"),$=e(D,"padding-right"),U=e(D,"margin-left"),Z=e(D,"margin-right"),ee=D.getPropertyValue("box-sizing");if(ee&&ee==="border-box")A=k+U+Z;else{const{clientWidth:ce,offsetWidth:Ae}=P;A=k+G+$+U+Z+(Ae-ce)}}O&&(P.style.transform=O),V&&(P.style.webkitTransform=V),t.roundLengths&&(A=Math.floor(A))}else A=(v-(t.slidesPerView-1)*x)/t.slidesPerView,t.roundLengths&&(A=Math.floor(A)),P&&(P.style[n.getDirectionLabel("width")]=`${A}px`);P&&(P.swiperSlideSize=A),f.push(A),t.centeredSlides?(w=w+A/2+S/2+x,S===0&&y!==0&&(w=w-v/2-x),y===0&&(w=w-v/2-x),Math.abs(w)<1/1e3&&(w=0),t.roundLengths&&(w=Math.floor(w)),C%t.slidesPerGroup===0&&d.push(w),p.push(w)):(t.roundLengths&&(w=Math.floor(w)),(C-Math.min(n.params.slidesPerGroupSkip,C))%n.params.slidesPerGroup===0&&d.push(w),p.push(w),w=w+A+x),n.virtualSize+=A+x,S=A,C+=1}}if(n.virtualSize=Math.max(n.virtualSize,v)+g,s&&o&&(t.effect==="slide"||t.effect==="coverflow")&&(i.style.width=`${n.virtualSize+x}px`),t.setWrapperSize&&(i.style[n.getDirectionLabel("width")]=`${n.virtualSize+x}px`),T&&n.grid.updateWrapperSize(A,d),!t.centeredSlides){const y=[];for(let P=0;P<d.length;P+=1){let D=d[P];t.roundLengths&&(D=Math.floor(D)),d[P]<=n.virtualSize-v&&y.push(D)}d=y,Math.floor(n.virtualSize-v)-Math.floor(d[d.length-1])>1&&d.push(n.virtualSize-v)}if(a&&t.loop){const y=f[0]+x;if(t.slidesPerGroup>1){const P=Math.ceil((n.virtual.slidesBefore+n.virtual.slidesAfter)/t.slidesPerGroup),D=y*t.slidesPerGroup;for(let O=0;O<P;O+=1)d.push(d[d.length-1]+D)}for(let P=0;P<n.virtual.slidesBefore+n.virtual.slidesAfter;P+=1)t.slidesPerGroup===1&&d.push(d[d.length-1]+y),p.push(p[p.length-1]+y),n.virtualSize+=y}if(d.length===0&&(d=[0]),x!==0){const y=n.isHorizontal()&&s?"marginLeft":n.getDirectionLabel("marginRight");c.filter((P,D)=>!t.cssMode||t.loop?!0:D!==c.length-1).forEach(P=>{P.style[y]=`${x}px`})}if(t.centeredSlides&&t.centeredSlidesBounds){let y=0;f.forEach(D=>{y+=D+(x||0)}),y-=x;const P=y>v?y-v:0;d=d.map(D=>D<=0?-_:D>P?P+g:D)}if(t.centerInsufficientSlides){let y=0;f.forEach(D=>{y+=D+(x||0)}),y-=x;const P=(_||0)+(g||0);if(y+P<v){const D=(v-y-P)/2;d.forEach((O,V)=>{d[V]=O-D}),p.forEach((O,V)=>{p[V]=O+D})}}if(Object.assign(n,{slides:c,snapGrid:d,slidesGrid:p,slidesSizesGrid:f}),t.centeredSlides&&t.cssMode&&!t.centeredSlidesBounds){So(i,"--swiper-centered-offset-before",`${-d[0]}px`),So(i,"--swiper-centered-offset-after",`${n.size/2-f[f.length-1]/2}px`);const y=-n.snapGrid[0],P=-n.slidesGrid[0];n.snapGrid=n.snapGrid.map(D=>D+y),n.slidesGrid=n.slidesGrid.map(D=>D+P)}if(u!==l&&n.emit("slidesLengthChange"),d.length!==m&&(n.params.watchOverflow&&n.checkOverflow(),n.emit("snapGridLengthChange")),p.length!==h&&n.emit("slidesGridLengthChange"),t.watchSlidesProgress&&n.updateSlidesOffset(),n.emit("slidesUpdated"),!a&&!t.cssMode&&(t.effect==="slide"||t.effect==="fade")){const y=`${t.containerModifierClass}backface-hidden`,P=n.el.classList.contains(y);u<=t.maxBackfaceHiddenSlides?P||n.el.classList.add(y):P&&n.el.classList.remove(y)}}function Vg(n){const e=this,t=[],i=e.virtual&&e.params.virtual.enabled;let r=0,s;typeof n=="number"?e.setTransition(n):n===!0&&e.setTransition(e.params.speed);const o=a=>i?e.slides[e.getSlideIndexByData(a)]:e.slides[a];if(e.params.slidesPerView!=="auto"&&e.params.slidesPerView>1)if(e.params.centeredSlides)(e.visibleSlides||[]).forEach(a=>{t.push(a)});else for(s=0;s<Math.ceil(e.params.slidesPerView);s+=1){const a=e.activeIndex+s;if(a>e.slides.length&&!i)break;t.push(o(a))}else t.push(o(e.activeIndex));for(s=0;s<t.length;s+=1)if(typeof t[s]<"u"){const a=t[s].offsetHeight;r=a>r?a:r}(r||r===0)&&(e.wrapperEl.style.height=`${r}px`)}function Hg(){const n=this,e=n.slides,t=n.isElement?n.isHorizontal()?n.wrapperEl.offsetLeft:n.wrapperEl.offsetTop:0;for(let i=0;i<e.length;i+=1)e[i].swiperSlideOffset=(n.isHorizontal()?e[i].offsetLeft:e[i].offsetTop)-t-n.cssOverflowAdjustment()}const Td=(n,e,t)=>{e&&!n.classList.contains(t)?n.classList.add(t):!e&&n.classList.contains(t)&&n.classList.remove(t)};function Gg(n=this&&this.translate||0){const e=this,t=e.params,{slides:i,rtlTranslate:r,snapGrid:s}=e;if(i.length===0)return;typeof i[0].swiperSlideOffset>"u"&&e.updateSlidesOffset();let o=-n;r&&(o=n),e.visibleSlidesIndexes=[],e.visibleSlides=[];let a=t.spaceBetween;typeof a=="string"&&a.indexOf("%")>=0?a=parseFloat(a.replace("%",""))/100*e.size:typeof a=="string"&&(a=parseFloat(a));for(let l=0;l<i.length;l+=1){const c=i[l];let u=c.swiperSlideOffset;t.cssMode&&t.centeredSlides&&(u-=i[0].swiperSlideOffset);const d=(o+(t.centeredSlides?e.minTranslate():0)-u)/(c.swiperSlideSize+a),p=(o-s[0]+(t.centeredSlides?e.minTranslate():0)-u)/(c.swiperSlideSize+a),f=-(o-u),_=f+e.slidesSizesGrid[l],g=f>=0&&f<=e.size-e.slidesSizesGrid[l],m=f>=0&&f<e.size-1||_>1&&_<=e.size||f<=0&&_>=e.size;m&&(e.visibleSlides.push(c),e.visibleSlidesIndexes.push(l)),Td(c,m,t.slideVisibleClass),Td(c,g,t.slideFullyVisibleClass),c.progress=r?-d:d,c.originalProgress=r?-p:p}}function Wg(n){const e=this;if(typeof n>"u"){const u=e.rtlTranslate?-1:1;n=e&&e.translate&&e.translate*u||0}const t=e.params,i=e.maxTranslate()-e.minTranslate();let{progress:r,isBeginning:s,isEnd:o,progressLoop:a}=e;const l=s,c=o;if(i===0)r=0,s=!0,o=!0;else{r=(n-e.minTranslate())/i;const u=Math.abs(n-e.minTranslate())<1,d=Math.abs(n-e.maxTranslate())<1;s=u||r<=0,o=d||r>=1,u&&(r=0),d&&(r=1)}if(t.loop){const u=e.getSlideIndexByData(0),d=e.getSlideIndexByData(e.slides.length-1),p=e.slidesGrid[u],f=e.slidesGrid[d],_=e.slidesGrid[e.slidesGrid.length-1],g=Math.abs(n);g>=p?a=(g-p)/_:a=(g+_-f)/_,a>1&&(a-=1)}Object.assign(e,{progress:r,progressLoop:a,isBeginning:s,isEnd:o}),(t.watchSlidesProgress||t.centeredSlides&&t.autoHeight)&&e.updateSlidesProgress(n),s&&!l&&e.emit("reachBeginning toEdge"),o&&!c&&e.emit("reachEnd toEdge"),(l&&!s||c&&!o)&&e.emit("fromEdge"),e.emit("progress",r)}const Ja=(n,e,t)=>{e&&!n.classList.contains(t)?n.classList.add(t):!e&&n.classList.contains(t)&&n.classList.remove(t)};function Xg(){const n=this,{slides:e,params:t,slidesEl:i,activeIndex:r}=n,s=n.virtual&&t.virtual.enabled,o=n.grid&&t.grid&&t.grid.rows>1,a=d=>$n(i,`.${t.slideClass}${d}, swiper-slide${d}`)[0];let l,c,u;if(s)if(t.loop){let d=r-n.virtual.slidesBefore;d<0&&(d=n.virtual.slides.length+d),d>=n.virtual.slides.length&&(d-=n.virtual.slides.length),l=a(`[data-swiper-slide-index="${d}"]`)}else l=a(`[data-swiper-slide-index="${r}"]`);else o?(l=e.find(d=>d.column===r),u=e.find(d=>d.column===r+1),c=e.find(d=>d.column===r-1)):l=e[r];l&&(o||(u=Lg(l,`.${t.slideClass}, swiper-slide`)[0],t.loop&&!u&&(u=e[0]),c=Dg(l,`.${t.slideClass}, swiper-slide`)[0],t.loop&&!c===0&&(c=e[e.length-1]))),e.forEach(d=>{Ja(d,d===l,t.slideActiveClass),Ja(d,d===u,t.slideNextClass),Ja(d,d===c,t.slidePrevClass)}),n.emitSlidesClasses()}const Zo=(n,e)=>{if(!n||n.destroyed||!n.params)return;const t=()=>n.isElement?"swiper-slide":`.${n.params.slideClass}`,i=e.closest(t());if(i){let r=i.querySelector(`.${n.params.lazyPreloaderClass}`);!r&&n.isElement&&(i.shadowRoot?r=i.shadowRoot.querySelector(`.${n.params.lazyPreloaderClass}`):requestAnimationFrame(()=>{i.shadowRoot&&(r=i.shadowRoot.querySelector(`.${n.params.lazyPreloaderClass}`),r&&r.remove())})),r&&r.remove()}},Qa=(n,e)=>{if(!n.slides[e])return;const t=n.slides[e].querySelector('[loading="lazy"]');t&&t.removeAttribute("loading")},Ql=n=>{if(!n||n.destroyed||!n.params)return;let e=n.params.lazyPreloadPrevNext;const t=n.slides.length;if(!t||!e||e<0)return;e=Math.min(e,t);const i=n.params.slidesPerView==="auto"?n.slidesPerViewDynamic():Math.ceil(n.params.slidesPerView),r=n.activeIndex;if(n.params.grid&&n.params.grid.rows>1){const o=r,a=[o-e];a.push(...Array.from({length:e}).map((l,c)=>o+i+c)),n.slides.forEach((l,c)=>{a.includes(l.column)&&Qa(n,c)});return}const s=r+i-1;if(n.params.rewind||n.params.loop)for(let o=r-e;o<=s+e;o+=1){const a=(o%t+t)%t;(a<r||a>s)&&Qa(n,a)}else for(let o=Math.max(r-e,0);o<=Math.min(s+e,t-1);o+=1)o!==r&&(o>s||o<r)&&Qa(n,o)};function $g(n){const{slidesGrid:e,params:t}=n,i=n.rtlTranslate?n.translate:-n.translate;let r;for(let s=0;s<e.length;s+=1)typeof e[s+1]<"u"?i>=e[s]&&i<e[s+1]-(e[s+1]-e[s])/2?r=s:i>=e[s]&&i<e[s+1]&&(r=s+1):i>=e[s]&&(r=s);return t.normalizeSlideIndex&&(r<0||typeof r>"u")&&(r=0),r}function qg(n){const e=this,t=e.rtlTranslate?e.translate:-e.translate,{snapGrid:i,params:r,activeIndex:s,realIndex:o,snapIndex:a}=e;let l=n,c;const u=f=>{let _=f-e.virtual.slidesBefore;return _<0&&(_=e.virtual.slides.length+_),_>=e.virtual.slides.length&&(_-=e.virtual.slides.length),_};if(typeof l>"u"&&(l=$g(e)),i.indexOf(t)>=0)c=i.indexOf(t);else{const f=Math.min(r.slidesPerGroupSkip,l);c=f+Math.floor((l-f)/r.slidesPerGroup)}if(c>=i.length&&(c=i.length-1),l===s&&!e.params.loop){c!==a&&(e.snapIndex=c,e.emit("snapIndexChange"));return}if(l===s&&e.params.loop&&e.virtual&&e.params.virtual.enabled){e.realIndex=u(l);return}const d=e.grid&&r.grid&&r.grid.rows>1;let p;if(e.virtual&&r.virtual.enabled&&r.loop)p=u(l);else if(d){const f=e.slides.find(g=>g.column===l);let _=parseInt(f.getAttribute("data-swiper-slide-index"),10);Number.isNaN(_)&&(_=Math.max(e.slides.indexOf(f),0)),p=Math.floor(_/r.grid.rows)}else if(e.slides[l]){const f=e.slides[l].getAttribute("data-swiper-slide-index");f?p=parseInt(f,10):p=l}else p=l;Object.assign(e,{previousSnapIndex:a,snapIndex:c,previousRealIndex:o,realIndex:p,previousIndex:s,activeIndex:l}),e.initialized&&Ql(e),e.emit("activeIndexChange"),e.emit("snapIndexChange"),(e.initialized||e.params.runCallbacksOnInit)&&(o!==p&&e.emit("realIndexChange"),e.emit("slideChange"))}function Yg(n,e){const t=this,i=t.params;let r=n.closest(`.${i.slideClass}, swiper-slide`);!r&&t.isElement&&e&&e.length>1&&e.includes(n)&&[...e.slice(e.indexOf(n)+1,e.length)].forEach(a=>{!r&&a.matches&&a.matches(`.${i.slideClass}, swiper-slide`)&&(r=a)});let s=!1,o;if(r){for(let a=0;a<t.slides.length;a+=1)if(t.slides[a]===r){s=!0,o=a;break}}if(r&&s)t.clickedSlide=r,t.virtual&&t.params.virtual.enabled?t.clickedIndex=parseInt(r.getAttribute("data-swiper-slide-index"),10):t.clickedIndex=o;else{t.clickedSlide=void 0,t.clickedIndex=void 0;return}i.slideToClickedSlide&&t.clickedIndex!==void 0&&t.clickedIndex!==t.activeIndex&&t.slideToClickedSlide()}var jg={updateSize:Bg,updateSlides:zg,updateAutoHeight:Vg,updateSlidesOffset:Hg,updateSlidesProgress:Gg,updateProgress:Wg,updateSlidesClasses:Xg,updateActiveIndex:qg,updateClickedSlide:Yg};function Kg(n=this.isHorizontal()?"x":"y"){const e=this,{params:t,rtlTranslate:i,translate:r,wrapperEl:s}=e;if(t.virtualTranslate)return i?-r:r;if(t.cssMode)return r;let o=Ag(s,n);return o+=e.cssOverflowAdjustment(),i&&(o=-o),o||0}function Zg(n,e){const t=this,{rtlTranslate:i,params:r,wrapperEl:s,progress:o}=t;let a=0,l=0;const c=0;t.isHorizontal()?a=i?-n:n:l=n,r.roundLengths&&(a=Math.floor(a),l=Math.floor(l)),t.previousTranslate=t.translate,t.translate=t.isHorizontal()?a:l,r.cssMode?s[t.isHorizontal()?"scrollLeft":"scrollTop"]=t.isHorizontal()?-a:-l:r.virtualTranslate||(t.isHorizontal()?a-=t.cssOverflowAdjustment():l-=t.cssOverflowAdjustment(),s.style.transform=`translate3d(${a}px, ${l}px, ${c}px)`);let u;const d=t.maxTranslate()-t.minTranslate();d===0?u=0:u=(n-t.minTranslate())/d,u!==o&&t.updateProgress(n),t.emit("setTranslate",t.translate,e)}function Jg(){return-this.snapGrid[0]}function Qg(){return-this.snapGrid[this.snapGrid.length-1]}function e_(n=0,e=this.params.speed,t=!0,i=!0,r){const s=this,{params:o,wrapperEl:a}=s;if(s.animating&&o.preventInteractionOnTransition)return!1;const l=s.minTranslate(),c=s.maxTranslate();let u;if(i&&n>l?u=l:i&&n<c?u=c:u=n,s.updateProgress(u),o.cssMode){const d=s.isHorizontal();if(e===0)a[d?"scrollLeft":"scrollTop"]=-u;else{if(!s.support.smoothScroll)return _f({swiper:s,targetPosition:-u,side:d?"left":"top"}),!0;a.scrollTo({[d?"left":"top"]:-u,behavior:"smooth"})}return!0}return e===0?(s.setTransition(0),s.setTranslate(u),t&&(s.emit("beforeTransitionStart",e,r),s.emit("transitionEnd"))):(s.setTransition(e),s.setTranslate(u),t&&(s.emit("beforeTransitionStart",e,r),s.emit("transitionStart")),s.animating||(s.animating=!0,s.onTranslateToWrapperTransitionEnd||(s.onTranslateToWrapperTransitionEnd=function(p){!s||s.destroyed||p.target===this&&(s.wrapperEl.removeEventListener("transitionend",s.onTranslateToWrapperTransitionEnd),s.onTranslateToWrapperTransitionEnd=null,delete s.onTranslateToWrapperTransitionEnd,s.animating=!1,t&&s.emit("transitionEnd"))}),s.wrapperEl.addEventListener("transitionend",s.onTranslateToWrapperTransitionEnd))),!0}var t_={getTranslate:Kg,setTranslate:Zg,minTranslate:Jg,maxTranslate:Qg,translateTo:e_};function n_(n,e){const t=this;t.params.cssMode||(t.wrapperEl.style.transitionDuration=`${n}ms`,t.wrapperEl.style.transitionDelay=n===0?"0ms":""),t.emit("setTransition",n,e)}function bf({swiper:n,runCallbacks:e,direction:t,step:i}){const{activeIndex:r,previousIndex:s}=n;let o=t;o||(r>s?o="next":r<s?o="prev":o="reset"),n.emit(`transition${i}`),e&&o==="reset"?n.emit(`slideResetTransition${i}`):e&&r!==s&&(n.emit(`slideChangeTransition${i}`),o==="next"?n.emit(`slideNextTransition${i}`):n.emit(`slidePrevTransition${i}`))}function i_(n=!0,e){const t=this,{params:i}=t;i.cssMode||(i.autoHeight&&t.updateAutoHeight(),bf({swiper:t,runCallbacks:n,direction:e,step:"Start"}))}function r_(n=!0,e){const t=this,{params:i}=t;t.animating=!1,!i.cssMode&&(t.setTransition(0),bf({swiper:t,runCallbacks:n,direction:e,step:"End"}))}var s_={setTransition:n_,transitionStart:i_,transitionEnd:r_};function o_(n=0,e,t=!0,i,r){typeof n=="string"&&(n=parseInt(n,10));const s=this;let o=n;o<0&&(o=0);const{params:a,snapGrid:l,slidesGrid:c,previousIndex:u,activeIndex:d,rtlTranslate:p,wrapperEl:f,enabled:_}=s;if(!_&&!i&&!r||s.destroyed||s.animating&&a.preventInteractionOnTransition)return!1;typeof e>"u"&&(e=s.params.speed);const g=Math.min(s.params.slidesPerGroupSkip,o);let m=g+Math.floor((o-g)/s.params.slidesPerGroup);m>=l.length&&(m=l.length-1);const h=-l[m];if(a.normalizeSlideIndex)for(let T=0;T<c.length;T+=1){const A=-Math.floor(h*100),b=Math.floor(c[T]*100),y=Math.floor(c[T+1]*100);typeof c[T+1]<"u"?A>=b&&A<y-(y-b)/2?o=T:A>=b&&A<y&&(o=T+1):A>=b&&(o=T)}if(s.initialized&&o!==d&&(!s.allowSlideNext&&(p?h>s.translate&&h>s.minTranslate():h<s.translate&&h<s.minTranslate())||!s.allowSlidePrev&&h>s.translate&&h>s.maxTranslate()&&(d||0)!==o))return!1;o!==(u||0)&&t&&s.emit("beforeSlideChangeStart"),s.updateProgress(h);let v;o>d?v="next":o<d?v="prev":v="reset";const x=s.virtual&&s.params.virtual.enabled;if(!(x&&r)&&(p&&-h===s.translate||!p&&h===s.translate))return s.updateActiveIndex(o),a.autoHeight&&s.updateAutoHeight(),s.updateSlidesClasses(),a.effect!=="slide"&&s.setTranslate(h),v!=="reset"&&(s.transitionStart(t,v),s.transitionEnd(t,v)),!1;if(a.cssMode){const T=s.isHorizontal(),A=p?h:-h;if(e===0)x&&(s.wrapperEl.style.scrollSnapType="none",s._immediateVirtual=!0),x&&!s._cssModeVirtualInitialSet&&s.params.initialSlide>0?(s._cssModeVirtualInitialSet=!0,requestAnimationFrame(()=>{f[T?"scrollLeft":"scrollTop"]=A})):f[T?"scrollLeft":"scrollTop"]=A,x&&requestAnimationFrame(()=>{s.wrapperEl.style.scrollSnapType="",s._immediateVirtual=!1});else{if(!s.support.smoothScroll)return _f({swiper:s,targetPosition:A,side:T?"left":"top"}),!0;f.scrollTo({[T?"left":"top"]:A,behavior:"smooth"})}return!0}const C=yf().isSafari;return x&&!r&&C&&s.isElement&&s.virtual.update(!1,!1,o),s.setTransition(e),s.setTranslate(h),s.updateActiveIndex(o),s.updateSlidesClasses(),s.emit("beforeTransitionStart",e,i),s.transitionStart(t,v),e===0?s.transitionEnd(t,v):s.animating||(s.animating=!0,s.onSlideToWrapperTransitionEnd||(s.onSlideToWrapperTransitionEnd=function(A){!s||s.destroyed||A.target===this&&(s.wrapperEl.removeEventListener("transitionend",s.onSlideToWrapperTransitionEnd),s.onSlideToWrapperTransitionEnd=null,delete s.onSlideToWrapperTransitionEnd,s.transitionEnd(t,v))}),s.wrapperEl.addEventListener("transitionend",s.onSlideToWrapperTransitionEnd)),!0}function a_(n=0,e,t=!0,i){typeof n=="string"&&(n=parseInt(n,10));const r=this;if(r.destroyed)return;typeof e>"u"&&(e=r.params.speed);const s=r.grid&&r.params.grid&&r.params.grid.rows>1;let o=n;if(r.params.loop)if(r.virtual&&r.params.virtual.enabled)o=o+r.virtual.slidesBefore;else{let a;if(s){const g=o*r.params.grid.rows;a=r.slides.find(m=>m.getAttribute("data-swiper-slide-index")*1===g).column}else a=r.getSlideIndexByData(o);const l=s?Math.ceil(r.slides.length/r.params.grid.rows):r.slides.length,{centeredSlides:c,slidesOffsetBefore:u,slidesOffsetAfter:d}=r.params,p=c||!!u||!!d;let f=r.params.slidesPerView;f==="auto"?f=r.slidesPerViewDynamic():(f=Math.ceil(parseFloat(r.params.slidesPerView,10)),p&&f%2===0&&(f=f+1));let _=l-a<f;if(p&&(_=_||a<Math.ceil(f/2)),i&&p&&r.params.slidesPerView!=="auto"&&!s&&(_=!1),_){const g=p?a<r.activeIndex?"prev":"next":a-r.activeIndex-1<r.params.slidesPerView?"next":"prev";r.loopFix({direction:g,slideTo:!0,activeSlideIndex:g==="next"?a+1:a-l+1,slideRealIndex:g==="next"?r.realIndex:void 0})}if(s){const g=o*r.params.grid.rows;o=r.slides.find(m=>m.getAttribute("data-swiper-slide-index")*1===g).column}else o=r.getSlideIndexByData(o)}return requestAnimationFrame(()=>{r.slideTo(o,e,t,i)}),r}function l_(n,e=!0,t){const i=this,{enabled:r,params:s,animating:o}=i;if(!r||i.destroyed)return i;typeof n>"u"&&(n=i.params.speed);let a=s.slidesPerGroup;s.slidesPerView==="auto"&&s.slidesPerGroup===1&&s.slidesPerGroupAuto&&(a=Math.max(i.slidesPerViewDynamic("current",!0),1));const l=i.activeIndex<s.slidesPerGroupSkip?1:a,c=i.virtual&&s.virtual.enabled;if(s.loop){if(o&&!c&&s.loopPreventsSliding)return!1;if(i.loopFix({direction:"next"}),i._clientLeft=i.wrapperEl.clientLeft,i.activeIndex===i.slides.length-1&&s.cssMode)return requestAnimationFrame(()=>{i.slideTo(i.activeIndex+l,n,e,t)}),!0}return s.rewind&&i.isEnd?i.slideTo(0,n,e,t):i.slideTo(i.activeIndex+l,n,e,t)}function c_(n,e=!0,t){const i=this,{params:r,snapGrid:s,slidesGrid:o,rtlTranslate:a,enabled:l,animating:c}=i;if(!l||i.destroyed)return i;typeof n>"u"&&(n=i.params.speed);const u=i.virtual&&r.virtual.enabled;if(r.loop){if(c&&!u&&r.loopPreventsSliding)return!1;i.loopFix({direction:"prev"}),i._clientLeft=i.wrapperEl.clientLeft}const d=a?i.translate:-i.translate;function p(v){return v<0?-Math.floor(Math.abs(v)):Math.floor(v)}const f=p(d),_=s.map(v=>p(v)),g=r.freeMode&&r.freeMode.enabled;let m=s[_.indexOf(f)-1];if(typeof m>"u"&&(r.cssMode||g)){let v;s.forEach((x,w)=>{f>=x&&(v=w)}),typeof v<"u"&&(m=g?s[v]:s[v>0?v-1:v])}let h=0;if(typeof m<"u"&&(h=o.indexOf(m),h<0&&(h=i.activeIndex-1),r.slidesPerView==="auto"&&r.slidesPerGroup===1&&r.slidesPerGroupAuto&&(h=h-i.slidesPerViewDynamic("previous",!0)+1,h=Math.max(h,0))),r.rewind&&i.isBeginning){const v=i.params.virtual&&i.params.virtual.enabled&&i.virtual?i.virtual.slides.length-1:i.slides.length-1;return i.slideTo(v,n,e,t)}else if(r.loop&&i.activeIndex===0&&r.cssMode)return requestAnimationFrame(()=>{i.slideTo(h,n,e,t)}),!0;return i.slideTo(h,n,e,t)}function u_(n,e=!0,t){const i=this;if(!i.destroyed)return typeof n>"u"&&(n=i.params.speed),i.slideTo(i.activeIndex,n,e,t)}function d_(n,e=!0,t,i=.5){const r=this;if(r.destroyed)return;typeof n>"u"&&(n=r.params.speed);let s=r.activeIndex;const o=Math.min(r.params.slidesPerGroupSkip,s),a=o+Math.floor((s-o)/r.params.slidesPerGroup),l=r.rtlTranslate?r.translate:-r.translate;if(l>=r.snapGrid[a]){const c=r.snapGrid[a],u=r.snapGrid[a+1];l-c>(u-c)*i&&(s+=r.params.slidesPerGroup)}else{const c=r.snapGrid[a-1],u=r.snapGrid[a];l-c<=(u-c)*i&&(s-=r.params.slidesPerGroup)}return s=Math.max(s,0),s=Math.min(s,r.slidesGrid.length-1),r.slideTo(s,n,e,t)}function h_(){const n=this;if(n.destroyed)return;const{params:e,slidesEl:t}=n,i=e.slidesPerView==="auto"?n.slidesPerViewDynamic():e.slidesPerView;let r=n.getSlideIndexWhenGrid(n.clickedIndex),s;const o=n.isElement?"swiper-slide":`.${e.slideClass}`,a=n.grid&&n.params.grid&&n.params.grid.rows>1;if(e.loop){if(n.animating)return;s=parseInt(n.clickedSlide.getAttribute("data-swiper-slide-index"),10),e.centeredSlides?n.slideToLoop(s):r>(a?(n.slides.length-i)/2-(n.params.grid.rows-1):n.slides.length-i)?(n.loopFix(),r=n.getSlideIndex($n(t,`${o}[data-swiper-slide-index="${s}"]`)[0]),gf(()=>{n.slideTo(r)})):n.slideTo(r)}else n.slideTo(r)}var f_={slideTo:o_,slideToLoop:a_,slideNext:l_,slidePrev:c_,slideReset:u_,slideToClosest:d_,slideToClickedSlide:h_};function p_(n,e){const t=this,{params:i,slidesEl:r}=t;if(!i.loop||t.virtual&&t.params.virtual.enabled)return;const s=()=>{$n(r,`.${i.slideClass}, swiper-slide`).forEach((_,g)=>{_.setAttribute("data-swiper-slide-index",g)})},o=()=>{const f=$n(r,`.${i.slideBlankClass}`);f.forEach(_=>{_.remove()}),f.length>0&&(t.recalcSlides(),t.updateSlides())},a=t.grid&&i.grid&&i.grid.rows>1;i.loopAddBlankSlides&&(i.slidesPerGroup>1||a)&&o();const l=i.slidesPerGroup*(a?i.grid.rows:1),c=t.slides.length%l!==0,u=a&&t.slides.length%i.grid.rows!==0,d=f=>{for(let _=0;_<f;_+=1){const g=t.isElement?ca("swiper-slide",[i.slideBlankClass]):ca("div",[i.slideClass,i.slideBlankClass]);t.slidesEl.append(g)}};if(c){if(i.loopAddBlankSlides){const f=l-t.slides.length%l;d(f),t.recalcSlides(),t.updateSlides()}else la("Swiper Loop Warning: The number of slides is not even to slidesPerGroup, loop mode may not function properly. You need to add more slides (or make duplicates, or empty slides)");s()}else if(u){if(i.loopAddBlankSlides){const f=i.grid.rows-t.slides.length%i.grid.rows;d(f),t.recalcSlides(),t.updateSlides()}else la("Swiper Loop Warning: The number of slides is not even to grid.rows, loop mode may not function properly. You need to add more slides (or make duplicates, or empty slides)");s()}else s();const p=i.centeredSlides||!!i.slidesOffsetBefore||!!i.slidesOffsetAfter;t.loopFix({slideRealIndex:n,direction:p?void 0:"next",initial:e})}function m_({slideRealIndex:n,slideTo:e=!0,direction:t,setTranslate:i,activeSlideIndex:r,initial:s,byController:o,byMousewheel:a}={}){const l=this;if(!l.params.loop)return;l.emit("beforeLoopFix");const{slides:c,allowSlidePrev:u,allowSlideNext:d,slidesEl:p,params:f}=l,{centeredSlides:_,slidesOffsetBefore:g,slidesOffsetAfter:m,initialSlide:h}=f,v=_||!!g||!!m;if(l.allowSlidePrev=!0,l.allowSlideNext=!0,l.virtual&&f.virtual.enabled){e&&(!v&&l.snapIndex===0?l.slideTo(l.virtual.slides.length,0,!1,!0):v&&l.snapIndex<f.slidesPerView?l.slideTo(l.virtual.slides.length+l.snapIndex,0,!1,!0):l.snapIndex===l.snapGrid.length-1&&l.slideTo(l.virtual.slidesBefore,0,!1,!0)),l.allowSlidePrev=u,l.allowSlideNext=d,l.emit("loopFix");return}let x=f.slidesPerView;x==="auto"?x=l.slidesPerViewDynamic():(x=Math.ceil(parseFloat(f.slidesPerView,10)),v&&x%2===0&&(x=x+1));const w=f.slidesPerGroupAuto?x:f.slidesPerGroup;let S=v?Math.max(w,Math.ceil(x/2)):w;S%w!==0&&(S+=w-S%w),S+=f.loopAdditionalSlides,l.loopedSlides=S;const C=l.grid&&f.grid&&f.grid.rows>1;c.length<x+S||l.params.effect==="cards"&&c.length<x+S*2?la("Swiper Loop Warning: The number of slides is not enough for loop mode, it will be disabled or not function properly. You need to add more slides (or make duplicates) or lower the values of slidesPerView and slidesPerGroup parameters"):C&&f.grid.fill==="row"&&la("Swiper Loop Warning: Loop mode is not compatible with grid.fill = `row`");const T=[],A=[],b=C?Math.ceil(c.length/f.grid.rows):c.length,y=s&&b-h<x&&!v;let P=y?h:l.activeIndex;typeof r>"u"?r=l.getSlideIndex(c.find(U=>U.classList.contains(f.slideActiveClass))):P=r;const D=t==="next"||!t,O=t==="prev"||!t;let V=0,k=0;const $=(C?c[r].column:r)+(v&&typeof i>"u"?-x/2+.5:0);if($<S){V=Math.max(S-$,w);for(let U=0;U<S-$;U+=1){const Z=U-Math.floor(U/b)*b;if(C){const ee=b-Z-1;for(let ce=c.length-1;ce>=0;ce-=1)c[ce].column===ee&&T.push(ce)}else T.push(b-Z-1)}}else if($+x>b-S){k=Math.max($-(b-S*2),w),y&&(k=Math.max(k,x-b+h+1));for(let U=0;U<k;U+=1){const Z=U-Math.floor(U/b)*b;C?c.forEach((ee,ce)=>{ee.column===Z&&A.push(ce)}):A.push(Z)}}if(l.__preventObserver__=!0,requestAnimationFrame(()=>{l.__preventObserver__=!1}),l.params.effect==="cards"&&c.length<x+S*2&&(A.includes(r)&&A.splice(A.indexOf(r),1),T.includes(r)&&T.splice(T.indexOf(r),1)),O&&T.forEach(U=>{c[U].swiperLoopMoveDOM=!0,p.prepend(c[U]),c[U].swiperLoopMoveDOM=!1}),D&&A.forEach(U=>{c[U].swiperLoopMoveDOM=!0,p.append(c[U]),c[U].swiperLoopMoveDOM=!1}),l.recalcSlides(),f.slidesPerView==="auto"?l.updateSlides():C&&(T.length>0&&O||A.length>0&&D)&&l.slides.forEach((U,Z)=>{l.grid.updateSlide(Z,U,l.slides)}),f.watchSlidesProgress&&l.updateSlidesOffset(),e){if(T.length>0&&O){if(typeof n>"u"){const U=l.slidesGrid[P],ee=l.slidesGrid[P+V]-U;a?l.setTranslate(l.translate-ee):(l.slideTo(P+Math.ceil(V),0,!1,!0),i&&(l.touchEventsData.startTranslate=l.touchEventsData.startTranslate-ee,l.touchEventsData.currentTranslate=l.touchEventsData.currentTranslate-ee))}else if(i){const U=C?T.length/f.grid.rows:T.length;l.slideTo(l.activeIndex+U,0,!1,!0),l.touchEventsData.currentTranslate=l.translate}}else if(A.length>0&&D)if(typeof n>"u"){const U=l.slidesGrid[P],ee=l.slidesGrid[P-k]-U;a?l.setTranslate(l.translate-ee):(l.slideTo(P-k,0,!1,!0),i&&(l.touchEventsData.startTranslate=l.touchEventsData.startTranslate-ee,l.touchEventsData.currentTranslate=l.touchEventsData.currentTranslate-ee))}else{const U=C?A.length/f.grid.rows:A.length;l.slideTo(l.activeIndex-U,0,!1,!0)}}if(l.allowSlidePrev=u,l.allowSlideNext=d,l.controller&&l.controller.control&&!o){const U={slideRealIndex:n,direction:t,setTranslate:i,activeSlideIndex:r,byController:!0};Array.isArray(l.controller.control)?l.controller.control.forEach(Z=>{!Z.destroyed&&Z.params.loop&&Z.loopFix({...U,slideTo:Z.params.slidesPerView===f.slidesPerView?e:!1})}):l.controller.control instanceof l.constructor&&l.controller.control.params.loop&&l.controller.control.loopFix({...U,slideTo:l.controller.control.params.slidesPerView===f.slidesPerView?e:!1})}l.emit("loopFix")}function g_(){const n=this,{params:e,slidesEl:t}=n;if(!e.loop||!t||n.virtual&&n.params.virtual.enabled)return;n.recalcSlides();const i=[];n.slides.forEach(r=>{const s=typeof r.swiperSlideIndex>"u"?r.getAttribute("data-swiper-slide-index")*1:r.swiperSlideIndex;i[s]=r}),n.slides.forEach(r=>{r.removeAttribute("data-swiper-slide-index")}),i.forEach(r=>{t.append(r)}),n.recalcSlides(),n.slideTo(n.realIndex,0)}var __={loopCreate:p_,loopFix:m_,loopDestroy:g_};function v_(n){const e=this;if(!e.params.simulateTouch||e.params.watchOverflow&&e.isLocked||e.params.cssMode)return;const t=e.params.touchEventsTarget==="container"?e.el:e.wrapperEl;e.isElement&&(e.__preventObserver__=!0),t.style.cursor="move",t.style.cursor=n?"grabbing":"grab",e.isElement&&requestAnimationFrame(()=>{e.__preventObserver__=!1})}function x_(){const n=this;n.params.watchOverflow&&n.isLocked||n.params.cssMode||(n.isElement&&(n.__preventObserver__=!0),n[n.params.touchEventsTarget==="container"?"el":"wrapperEl"].style.cursor="",n.isElement&&requestAnimationFrame(()=>{n.__preventObserver__=!1}))}var w_={setGrabCursor:v_,unsetGrabCursor:x_};function y_(n,e=this){function t(i){if(!i||i===yr()||i===Kt())return null;i.assignedSlot&&(i=i.assignedSlot);const r=i.closest(n);return!r&&!i.getRootNode?null:r||t(i.getRootNode().host)}return t(e)}function Ad(n,e,t){const i=Kt(),{params:r}=n,s=r.edgeSwipeDetection,o=r.edgeSwipeThreshold;return s&&(t<=o||t>=i.innerWidth-o)?s==="prevent"?(e.preventDefault(),!0):!1:!0}function b_(n){const e=this,t=yr();let i=n;i.originalEvent&&(i=i.originalEvent);const r=e.touchEventsData;if(i.type==="pointerdown"){if(r.pointerId!==null&&r.pointerId!==i.pointerId)return;r.pointerId=i.pointerId}else i.type==="touchstart"&&i.targetTouches.length===1&&(r.touchId=i.targetTouches[0].identifier);if(i.type==="touchstart"){Ad(e,i,i.targetTouches[0].pageX);return}const{params:s,touches:o,enabled:a}=e;if(!a||!s.simulateTouch&&i.pointerType==="mouse"||e.animating&&s.preventInteractionOnTransition)return;!e.animating&&s.cssMode&&s.loop&&e.loopFix();let l=i.target;if(s.touchEventsTarget==="wrapper"&&!Rg(l,e.wrapperEl)||"which"in i&&i.which===3||"button"in i&&i.button>0||r.isTouched&&r.isMoved)return;const c=!!s.noSwipingClass&&s.noSwipingClass!=="",u=i.composedPath?i.composedPath():i.path;c&&i.target&&i.target.shadowRoot&&u&&(l=u[0]);const d=s.noSwipingSelector?s.noSwipingSelector:`.${s.noSwipingClass}`,p=!!(i.target&&i.target.shadowRoot);if(s.noSwiping&&(p?y_(d,l):l.closest(d))){e.allowClick=!0;return}if(s.swipeHandler&&!l.closest(s.swipeHandler))return;o.currentX=i.pageX,o.currentY=i.pageY;const f=o.currentX,_=o.currentY;if(!Ad(e,i,f))return;Object.assign(r,{isTouched:!0,isMoved:!1,allowTouchCallbacks:!0,isScrolling:void 0,startMoving:void 0}),o.startX=f,o.startY=_,r.touchStartTime=aa(),e.allowClick=!0,e.updateSize(),e.swipeDirection=void 0,s.threshold>0&&(r.allowThresholdMove=!1);let g=!0;l.matches(r.focusableElements)&&(g=!1,l.nodeName==="SELECT"&&(r.isTouched=!1)),t.activeElement&&t.activeElement.matches(r.focusableElements)&&t.activeElement!==l&&(i.pointerType==="mouse"||i.pointerType!=="mouse"&&!l.matches(r.focusableElements))&&t.activeElement.blur();const m=g&&e.allowTouchMove&&s.touchStartPreventDefault;(s.touchStartForcePreventDefault||m)&&!l.isContentEditable&&i.preventDefault(),s.freeMode&&s.freeMode.enabled&&e.freeMode&&e.animating&&!s.cssMode&&e.freeMode.onTouchStart(),e.emit("touchStart",i)}function S_(n){const e=yr(),t=this,i=t.touchEventsData,{params:r,touches:s,rtlTranslate:o,enabled:a}=t;if(!a||!r.simulateTouch&&n.pointerType==="mouse")return;let l=n;if(l.originalEvent&&(l=l.originalEvent),l.type==="pointermove"&&(i.touchId!==null||l.pointerId!==i.pointerId))return;let c;if(l.type==="touchmove"){if(c=[...l.changedTouches].find(S=>S.identifier===i.touchId),!c||c.identifier!==i.touchId)return}else c=l;if(!i.isTouched){i.startMoving&&i.isScrolling&&t.emit("touchMoveOpposite",l);return}const u=c.pageX,d=c.pageY;if(l.preventedByNestedSwiper){s.startX=u,s.startY=d;return}if(!t.allowTouchMove){l.target.matches(i.focusableElements)||(t.allowClick=!1),i.isTouched&&(Object.assign(s,{startX:u,startY:d,currentX:u,currentY:d}),i.touchStartTime=aa());return}if(r.touchReleaseOnEdges&&!r.loop)if(t.isVertical()){if(d<s.startY&&t.translate<=t.maxTranslate()||d>s.startY&&t.translate>=t.minTranslate()){i.isTouched=!1,i.isMoved=!1;return}}else{if(o&&(u>s.startX&&-t.translate<=t.maxTranslate()||u<s.startX&&-t.translate>=t.minTranslate()))return;if(!o&&(u<s.startX&&t.translate<=t.maxTranslate()||u>s.startX&&t.translate>=t.minTranslate()))return}if(e.activeElement&&e.activeElement.matches(i.focusableElements)&&e.activeElement!==l.target&&l.pointerType!=="mouse"&&e.activeElement.blur(),e.activeElement&&l.target===e.activeElement&&l.target.matches(i.focusableElements)){i.isMoved=!0,t.allowClick=!1;return}i.allowTouchCallbacks&&t.emit("touchMove",l),s.previousX=s.currentX,s.previousY=s.currentY,s.currentX=u,s.currentY=d;const p=s.currentX-s.startX,f=s.currentY-s.startY;if(t.params.threshold&&Math.sqrt(p**2+f**2)<t.params.threshold)return;if(typeof i.isScrolling>"u"){let S;t.isHorizontal()&&s.currentY===s.startY||t.isVertical()&&s.currentX===s.startX?i.isScrolling=!1:p*p+f*f>=25&&(S=Math.atan2(Math.abs(f),Math.abs(p))*180/Math.PI,i.isScrolling=t.isHorizontal()?S>r.touchAngle:90-S>r.touchAngle)}if(i.isScrolling&&t.emit("touchMoveOpposite",l),typeof i.startMoving>"u"&&(s.currentX!==s.startX||s.currentY!==s.startY)&&(i.startMoving=!0),i.isScrolling||l.type==="touchmove"&&i.preventTouchMoveFromPointerMove){i.isTouched=!1;return}if(!i.startMoving)return;t.allowClick=!1,!r.cssMode&&l.cancelable&&l.preventDefault(),r.touchMoveStopPropagation&&!r.nested&&l.stopPropagation();let _=t.isHorizontal()?p:f,g=t.isHorizontal()?s.currentX-s.previousX:s.currentY-s.previousY;r.oneWayMovement&&(_=Math.abs(_)*(o?1:-1),g=Math.abs(g)*(o?1:-1)),s.diff=_,_*=r.touchRatio,o&&(_=-_,g=-g);const m=t.touchesDirection;t.swipeDirection=_>0?"prev":"next",t.touchesDirection=g>0?"prev":"next";const h=t.params.loop&&!r.cssMode,v=t.touchesDirection==="next"&&t.allowSlideNext||t.touchesDirection==="prev"&&t.allowSlidePrev;if(!i.isMoved){if(h&&v&&t.loopFix({direction:t.swipeDirection}),i.startTranslate=t.getTranslate(),t.setTransition(0),t.animating){const S=new window.CustomEvent("transitionend",{bubbles:!0,cancelable:!0,detail:{bySwiperTouchMove:!0}});t.wrapperEl.dispatchEvent(S)}i.allowMomentumBounce=!1,r.grabCursor&&(t.allowSlideNext===!0||t.allowSlidePrev===!0)&&t.setGrabCursor(!0),t.emit("sliderFirstMove",l)}if(new Date().getTime(),r._loopSwapReset!==!1&&i.isMoved&&i.allowThresholdMove&&m!==t.touchesDirection&&h&&v&&Math.abs(_)>=1){Object.assign(s,{startX:u,startY:d,currentX:u,currentY:d,startTranslate:i.currentTranslate}),i.loopSwapReset=!0,i.startTranslate=i.currentTranslate;return}t.emit("sliderMove",l),i.isMoved=!0,i.currentTranslate=_+i.startTranslate;let x=!0,w=r.resistanceRatio;if(r.touchReleaseOnEdges&&(w=0),_>0?(h&&v&&i.allowThresholdMove&&i.currentTranslate>(r.centeredSlides?t.minTranslate()-t.slidesSizesGrid[t.activeIndex+1]-(r.slidesPerView!=="auto"&&t.slides.length-r.slidesPerView>=2?t.slidesSizesGrid[t.activeIndex+1]+t.params.spaceBetween:0)-t.params.spaceBetween:t.minTranslate())&&t.loopFix({direction:"prev",setTranslate:!0,activeSlideIndex:0}),i.currentTranslate>t.minTranslate()&&(x=!1,r.resistance&&(i.currentTranslate=t.minTranslate()-1+(-t.minTranslate()+i.startTranslate+_)**w))):_<0&&(h&&v&&i.allowThresholdMove&&i.currentTranslate<(r.centeredSlides?t.maxTranslate()+t.slidesSizesGrid[t.slidesSizesGrid.length-1]+t.params.spaceBetween+(r.slidesPerView!=="auto"&&t.slides.length-r.slidesPerView>=2?t.slidesSizesGrid[t.slidesSizesGrid.length-1]+t.params.spaceBetween:0):t.maxTranslate())&&t.loopFix({direction:"next",setTranslate:!0,activeSlideIndex:t.slides.length-(r.slidesPerView==="auto"?t.slidesPerViewDynamic():Math.ceil(parseFloat(r.slidesPerView,10)))}),i.currentTranslate<t.maxTranslate()&&(x=!1,r.resistance&&(i.currentTranslate=t.maxTranslate()+1-(t.maxTranslate()-i.startTranslate-_)**w))),x&&(l.preventedByNestedSwiper=!0),!t.allowSlideNext&&t.swipeDirection==="next"&&i.currentTranslate<i.startTranslate&&(i.currentTranslate=i.startTranslate),!t.allowSlidePrev&&t.swipeDirection==="prev"&&i.currentTranslate>i.startTranslate&&(i.currentTranslate=i.startTranslate),!t.allowSlidePrev&&!t.allowSlideNext&&(i.currentTranslate=i.startTranslate),r.threshold>0)if(Math.abs(_)>r.threshold||i.allowThresholdMove){if(!i.allowThresholdMove){i.allowThresholdMove=!0,s.startX=s.currentX,s.startY=s.currentY,i.currentTranslate=i.startTranslate,s.diff=t.isHorizontal()?s.currentX-s.startX:s.currentY-s.startY;return}}else{i.currentTranslate=i.startTranslate;return}!r.followFinger||r.cssMode||((r.freeMode&&r.freeMode.enabled&&t.freeMode||r.watchSlidesProgress)&&(t.updateActiveIndex(),t.updateSlidesClasses()),r.freeMode&&r.freeMode.enabled&&t.freeMode&&t.freeMode.onTouchMove(),t.updateProgress(i.currentTranslate),t.setTranslate(i.currentTranslate))}function E_(n){const e=this,t=e.touchEventsData;let i=n;i.originalEvent&&(i=i.originalEvent);let r;if(i.type==="touchend"||i.type==="touchcancel"){if(r=[...i.changedTouches].find(S=>S.identifier===t.touchId),!r||r.identifier!==t.touchId)return}else{if(t.touchId!==null||i.pointerId!==t.pointerId)return;r=i}if(["pointercancel","pointerout","pointerleave","contextmenu"].includes(i.type)&&!(["pointercancel","contextmenu"].includes(i.type)&&(e.browser.isSafari||e.browser.isWebView)))return;t.pointerId=null,t.touchId=null;const{params:o,touches:a,rtlTranslate:l,slidesGrid:c,enabled:u}=e;if(!u||!o.simulateTouch&&i.pointerType==="mouse")return;if(t.allowTouchCallbacks&&e.emit("touchEnd",i),t.allowTouchCallbacks=!1,!t.isTouched){t.isMoved&&o.grabCursor&&e.setGrabCursor(!1),t.isMoved=!1,t.startMoving=!1;return}o.grabCursor&&t.isMoved&&t.isTouched&&(e.allowSlideNext===!0||e.allowSlidePrev===!0)&&e.setGrabCursor(!1);const d=aa(),p=d-t.touchStartTime;if(e.allowClick){const S=i.path||i.composedPath&&i.composedPath();e.updateClickedSlide(S&&S[0]||i.target,S),e.emit("tap click",i),p<300&&d-t.lastClickTime<300&&e.emit("doubleTap doubleClick",i)}if(t.lastClickTime=aa(),gf(()=>{e.destroyed||(e.allowClick=!0)}),!t.isTouched||!t.isMoved||!e.swipeDirection||a.diff===0&&!t.loopSwapReset||t.currentTranslate===t.startTranslate&&!t.loopSwapReset){t.isTouched=!1,t.isMoved=!1,t.startMoving=!1;return}t.isTouched=!1,t.isMoved=!1,t.startMoving=!1;let f;if(o.followFinger?f=l?e.translate:-e.translate:f=-t.currentTranslate,o.cssMode)return;if(o.freeMode&&o.freeMode.enabled){e.freeMode.onTouchEnd({currentPos:f});return}const _=f>=-e.maxTranslate()&&!e.params.loop;let g=0,m=e.slidesSizesGrid[0];for(let S=0;S<c.length;S+=S<o.slidesPerGroupSkip?1:o.slidesPerGroup){const C=S<o.slidesPerGroupSkip-1?1:o.slidesPerGroup;typeof c[S+C]<"u"?(_||f>=c[S]&&f<c[S+C])&&(g=S,m=c[S+C]-c[S]):(_||f>=c[S])&&(g=S,m=c[c.length-1]-c[c.length-2])}let h=null,v=null;o.rewind&&(e.isBeginning?v=o.virtual&&o.virtual.enabled&&e.virtual?e.virtual.slides.length-1:e.slides.length-1:e.isEnd&&(h=0));const x=(f-c[g])/m,w=g<o.slidesPerGroupSkip-1?1:o.slidesPerGroup;if(p>o.longSwipesMs){if(!o.longSwipes){e.slideTo(e.activeIndex);return}e.swipeDirection==="next"&&(x>=o.longSwipesRatio?e.slideTo(o.rewind&&e.isEnd?h:g+w):e.slideTo(g)),e.swipeDirection==="prev"&&(x>1-o.longSwipesRatio?e.slideTo(g+w):v!==null&&x<0&&Math.abs(x)>o.longSwipesRatio?e.slideTo(v):e.slideTo(g))}else{if(!o.shortSwipes){e.slideTo(e.activeIndex);return}e.navigation&&(i.target===e.navigation.nextEl||i.target===e.navigation.prevEl)?i.target===e.navigation.nextEl?e.slideTo(g+w):e.slideTo(g):(e.swipeDirection==="next"&&e.slideTo(h!==null?h:g+w),e.swipeDirection==="prev"&&e.slideTo(v!==null?v:g))}}function Cd(){const n=this,{params:e,el:t}=n;if(t&&t.offsetWidth===0)return;e.breakpoints&&n.setBreakpoint();const{allowSlideNext:i,allowSlidePrev:r,snapGrid:s}=n,o=n.virtual&&n.params.virtual.enabled;n.allowSlideNext=!0,n.allowSlidePrev=!0,n.updateSize(),n.updateSlides(),n.updateSlidesClasses();const a=o&&e.loop;(e.slidesPerView==="auto"||e.slidesPerView>1)&&n.isEnd&&!n.isBeginning&&!n.params.centeredSlides&&!a?n.slideTo(n.slides.length-1,0,!1,!0):n.params.loop&&!o?n.slideToLoop(n.realIndex,0,!1,!0):n.slideTo(n.activeIndex,0,!1,!0),n.autoplay&&n.autoplay.running&&n.autoplay.paused&&(clearTimeout(n.autoplay.resizeTimeout),n.autoplay.resizeTimeout=setTimeout(()=>{n.autoplay&&n.autoplay.running&&n.autoplay.paused&&n.autoplay.resume()},500)),n.allowSlidePrev=r,n.allowSlideNext=i,n.params.watchOverflow&&s!==n.snapGrid&&n.checkOverflow()}function M_(n){const e=this;e.enabled&&(e.allowClick||(e.params.preventClicks&&n.preventDefault(),e.params.preventClicksPropagation&&e.animating&&(n.stopPropagation(),n.stopImmediatePropagation())))}function T_(){const n=this,{wrapperEl:e,rtlTranslate:t,enabled:i}=n;if(!i)return;n.previousTranslate=n.translate,n.isHorizontal()?n.translate=-e.scrollLeft:n.translate=-e.scrollTop,n.translate===0&&(n.translate=0),n.updateActiveIndex(),n.updateSlidesClasses();let r;const s=n.maxTranslate()-n.minTranslate();s===0?r=0:r=(n.translate-n.minTranslate())/s,r!==n.progress&&n.updateProgress(t?-n.translate:n.translate),n.emit("setTranslate",n.translate,!1)}function A_(n){const e=this;Zo(e,n.target),!(e.params.cssMode||e.params.slidesPerView!=="auto"&&!e.params.autoHeight)&&e.update()}function C_(){const n=this;n.documentTouchHandlerProceeded||(n.documentTouchHandlerProceeded=!0,n.params.touchReleaseOnEdges&&(n.el.style.touchAction="auto"))}const Sf=(n,e)=>{const t=yr(),{params:i,el:r,wrapperEl:s,device:o}=n,a=!!i.nested,l=e==="on"?"addEventListener":"removeEventListener",c=e;!r||typeof r=="string"||(t[l]("touchstart",n.onDocumentTouchStart,{passive:!1,capture:a}),r[l]("touchstart",n.onTouchStart,{passive:!1}),r[l]("pointerdown",n.onTouchStart,{passive:!1}),t[l]("touchmove",n.onTouchMove,{passive:!1,capture:a}),t[l]("pointermove",n.onTouchMove,{passive:!1,capture:a}),t[l]("touchend",n.onTouchEnd,{passive:!0}),t[l]("pointerup",n.onTouchEnd,{passive:!0}),t[l]("pointercancel",n.onTouchEnd,{passive:!0}),t[l]("touchcancel",n.onTouchEnd,{passive:!0}),t[l]("pointerout",n.onTouchEnd,{passive:!0}),t[l]("pointerleave",n.onTouchEnd,{passive:!0}),t[l]("contextmenu",n.onTouchEnd,{passive:!0}),(i.preventClicks||i.preventClicksPropagation)&&r[l]("click",n.onClick,!0),i.cssMode&&s[l]("scroll",n.onScroll),i.updateOnWindowResize?n[c](o.ios||o.android?"resize orientationchange observerUpdate":"resize observerUpdate",Cd,!0):n[c]("observerUpdate",Cd,!0),r[l]("load",n.onLoad,{capture:!0}))};function P_(){const n=this,{params:e}=n;n.onTouchStart=b_.bind(n),n.onTouchMove=S_.bind(n),n.onTouchEnd=E_.bind(n),n.onDocumentTouchStart=C_.bind(n),e.cssMode&&(n.onScroll=T_.bind(n)),n.onClick=M_.bind(n),n.onLoad=A_.bind(n),Sf(n,"on")}function R_(){Sf(this,"off")}var D_={attachEvents:P_,detachEvents:R_};const Pd=(n,e)=>n.grid&&e.grid&&e.grid.rows>1;function L_(){const n=this,{realIndex:e,initialized:t,params:i,el:r}=n,s=i.breakpoints;if(!s||s&&Object.keys(s).length===0)return;const o=yr(),a=i.breakpointsBase==="window"||!i.breakpointsBase?i.breakpointsBase:"container",l=["window","container"].includes(i.breakpointsBase)||!i.breakpointsBase?n.el:o.querySelector(i.breakpointsBase),c=n.getBreakpoint(s,a,l);if(!c||n.currentBreakpoint===c)return;const d=(c in s?s[c]:void 0)||n.originalParams,p=Pd(n,i),f=Pd(n,d),_=n.params.grabCursor,g=d.grabCursor,m=i.enabled;p&&!f?(r.classList.remove(`${i.containerModifierClass}grid`,`${i.containerModifierClass}grid-column`),n.emitContainerClasses()):!p&&f&&(r.classList.add(`${i.containerModifierClass}grid`),(d.grid.fill&&d.grid.fill==="column"||!d.grid.fill&&i.grid.fill==="column")&&r.classList.add(`${i.containerModifierClass}grid-column`),n.emitContainerClasses()),_&&!g?n.unsetGrabCursor():!_&&g&&n.setGrabCursor(),["navigation","pagination","scrollbar"].forEach(C=>{if(typeof d[C]>"u")return;const T=i[C]&&i[C].enabled,A=d[C]&&d[C].enabled;T&&!A&&n[C].disable(),!T&&A&&n[C].enable()});const h=d.direction&&d.direction!==i.direction,v=i.loop&&(d.slidesPerView!==i.slidesPerView||h),x=i.loop;h&&t&&n.changeDirection(),hn(n.params,d);const w=n.params.enabled,S=n.params.loop;Object.assign(n,{allowTouchMove:n.params.allowTouchMove,allowSlideNext:n.params.allowSlideNext,allowSlidePrev:n.params.allowSlidePrev}),m&&!w?n.disable():!m&&w&&n.enable(),n.currentBreakpoint=c,n.emit("_beforeBreakpoint",d),t&&(v?(n.loopDestroy(),n.loopCreate(e),n.updateSlides()):!x&&S?(n.loopCreate(e),n.updateSlides()):x&&!S&&n.loopDestroy()),n.emit("breakpoint",d)}function I_(n,e="window",t){if(!n||e==="container"&&!t)return;let i=!1;const r=Kt(),s=e==="window"?r.innerHeight:t.clientHeight,o=Object.keys(n).map(a=>{if(typeof a=="string"&&a.indexOf("@")===0){const l=parseFloat(a.substr(1));return{value:s*l,point:a}}return{value:a,point:a}});o.sort((a,l)=>parseInt(a.value,10)-parseInt(l.value,10));for(let a=0;a<o.length;a+=1){const{point:l,value:c}=o[a];e==="window"?r.matchMedia(`(min-width: ${c}px)`).matches&&(i=l):c<=t.clientWidth&&(i=l)}return i||"max"}var U_={setBreakpoint:L_,getBreakpoint:I_};function O_(n,e){const t=[];return n.forEach(i=>{typeof i=="object"?Object.keys(i).forEach(r=>{i[r]&&t.push(e+r)}):typeof i=="string"&&t.push(e+i)}),t}function F_(){const n=this,{classNames:e,params:t,rtl:i,el:r,device:s}=n,o=O_(["initialized",t.direction,{"free-mode":n.params.freeMode&&t.freeMode.enabled},{autoheight:t.autoHeight},{rtl:i},{grid:t.grid&&t.grid.rows>1},{"grid-column":t.grid&&t.grid.rows>1&&t.grid.fill==="column"},{android:s.android},{ios:s.ios},{"css-mode":t.cssMode},{centered:t.cssMode&&t.centeredSlides},{"watch-progress":t.watchSlidesProgress}],t.containerModifierClass);e.push(...o),r.classList.add(...e),n.emitContainerClasses()}function N_(){const n=this,{el:e,classNames:t}=n;!e||typeof e=="string"||(e.classList.remove(...t),n.emitContainerClasses())}var k_={addClasses:F_,removeClasses:N_};function B_(){const n=this,{isLocked:e,params:t}=n,{slidesOffsetBefore:i}=t;if(i){const r=n.slides.length-1,s=n.slidesGrid[r]+n.slidesSizesGrid[r]+i*2;n.isLocked=n.size>s}else n.isLocked=n.snapGrid.length===1;t.allowSlideNext===!0&&(n.allowSlideNext=!n.isLocked),t.allowSlidePrev===!0&&(n.allowSlidePrev=!n.isLocked),e&&e!==n.isLocked&&(n.isEnd=!1),e!==n.isLocked&&n.emit(n.isLocked?"lock":"unlock")}var z_={checkOverflow:B_},Rd={init:!0,direction:"horizontal",oneWayMovement:!1,swiperElementNodeName:"SWIPER-CONTAINER",touchEventsTarget:"wrapper",initialSlide:0,speed:300,cssMode:!1,updateOnWindowResize:!0,resizeObserver:!0,nested:!1,createElements:!1,eventsPrefix:"swiper",enabled:!0,focusableElements:"input, select, option, textarea, button, video, label",width:null,height:null,preventInteractionOnTransition:!1,userAgent:null,url:null,edgeSwipeDetection:!1,edgeSwipeThreshold:20,autoHeight:!1,setWrapperSize:!1,virtualTranslate:!1,effect:"slide",breakpoints:void 0,breakpointsBase:"window",spaceBetween:0,slidesPerView:1,slidesPerGroup:1,slidesPerGroupSkip:0,slidesPerGroupAuto:!1,centeredSlides:!1,centeredSlidesBounds:!1,slidesOffsetBefore:0,slidesOffsetAfter:0,normalizeSlideIndex:!0,centerInsufficientSlides:!1,watchOverflow:!0,roundLengths:!1,touchRatio:1,touchAngle:45,simulateTouch:!0,shortSwipes:!0,longSwipes:!0,longSwipesRatio:.5,longSwipesMs:300,followFinger:!0,allowTouchMove:!0,threshold:5,touchMoveStopPropagation:!1,touchStartPreventDefault:!0,touchStartForcePreventDefault:!1,touchReleaseOnEdges:!1,uniqueNavElements:!0,resistance:!0,resistanceRatio:.85,watchSlidesProgress:!1,grabCursor:!1,preventClicks:!0,preventClicksPropagation:!0,slideToClickedSlide:!1,loop:!1,loopAddBlankSlides:!0,loopAdditionalSlides:0,loopPreventsSliding:!0,rewind:!1,allowSlidePrev:!0,allowSlideNext:!0,swipeHandler:null,noSwiping:!0,noSwipingClass:"swiper-no-swiping",noSwipingSelector:null,passiveListeners:!0,maxBackfaceHiddenSlides:10,containerModifierClass:"swiper-",slideClass:"swiper-slide",slideBlankClass:"swiper-slide-blank",slideActiveClass:"swiper-slide-active",slideVisibleClass:"swiper-slide-visible",slideFullyVisibleClass:"swiper-slide-fully-visible",slideNextClass:"swiper-slide-next",slidePrevClass:"swiper-slide-prev",wrapperClass:"swiper-wrapper",lazyPreloaderClass:"swiper-lazy-preloader",lazyPreloadPrevNext:0,runCallbacksOnInit:!0,_emitClasses:!1};function V_(n,e){return function(i={}){const r=Object.keys(i)[0],s=i[r];if(typeof s!="object"||s===null){hn(e,i);return}if(n[r]===!0&&(n[r]={enabled:!0}),r==="navigation"&&n[r]&&n[r].enabled&&!n[r].prevEl&&!n[r].nextEl&&(n[r].auto=!0),["pagination","scrollbar"].indexOf(r)>=0&&n[r]&&n[r].enabled&&!n[r].el&&(n[r].auto=!0),!(r in n&&"enabled"in s)){hn(e,i);return}typeof n[r]=="object"&&!("enabled"in n[r])&&(n[r].enabled=!0),n[r]||(n[r]={enabled:!1}),hn(e,i)}}const el={eventsEmitter:kg,update:jg,translate:t_,transition:s_,slide:f_,loop:__,grabCursor:w_,events:D_,breakpoints:U_,checkOverflow:z_,classes:k_},tl={};class Tn{constructor(...e){let t,i;e.length===1&&e[0].constructor&&Object.prototype.toString.call(e[0]).slice(8,-1)==="Object"?i=e[0]:[t,i]=e,i||(i={}),i=hn({},i),t&&!i.el&&(i.el=t);const r=yr();if(i.el&&typeof i.el=="string"&&r.querySelectorAll(i.el).length>1){const l=[];return r.querySelectorAll(i.el).forEach(c=>{const u=hn({},i,{el:c});l.push(new Tn(u))}),l}const s=this;s.__swiper__=!0,s.support=xf(),s.device=wf({userAgent:i.userAgent}),s.browser=yf(),s.eventsListeners={},s.eventsAnyListeners=[],s.modules=[...s.__modules__],i.modules&&Array.isArray(i.modules)&&s.modules.push(...i.modules);const o={};s.modules.forEach(l=>{l({params:i,swiper:s,extendParams:V_(i,o),on:s.on.bind(s),once:s.once.bind(s),off:s.off.bind(s),emit:s.emit.bind(s)})});const a=hn({},Rd,o);return s.params=hn({},a,tl,i),s.originalParams=hn({},s.params),s.passedParams=hn({},i),s.params&&s.params.on&&Object.keys(s.params.on).forEach(l=>{s.on(l,s.params.on[l])}),s.params&&s.params.onAny&&s.onAny(s.params.onAny),Object.assign(s,{enabled:s.params.enabled,el:t,classNames:[],slides:[],slidesGrid:[],snapGrid:[],slidesSizesGrid:[],isHorizontal(){return s.params.direction==="horizontal"},isVertical(){return s.params.direction==="vertical"},activeIndex:0,realIndex:0,isBeginning:!0,isEnd:!1,translate:0,previousTranslate:0,progress:0,velocity:0,animating:!1,cssOverflowAdjustment(){return Math.trunc(this.translate/2**23)*2**23},allowSlideNext:s.params.allowSlideNext,allowSlidePrev:s.params.allowSlidePrev,touchEventsData:{isTouched:void 0,isMoved:void 0,allowTouchCallbacks:void 0,touchStartTime:void 0,isScrolling:void 0,currentTranslate:void 0,startTranslate:void 0,allowThresholdMove:void 0,focusableElements:s.params.focusableElements,lastClickTime:0,clickTimeout:void 0,velocities:[],allowMomentumBounce:void 0,startMoving:void 0,pointerId:null,touchId:null},allowClick:!0,allowTouchMove:s.params.allowTouchMove,touches:{startX:0,startY:0,currentX:0,currentY:0,diff:0},imagesToLoad:[],imagesLoaded:0}),s.emit("_swiper"),s.params.init&&s.init(),s}getDirectionLabel(e){return this.isHorizontal()?e:{width:"height","margin-top":"margin-left","margin-bottom ":"margin-right","margin-left":"margin-top","margin-right":"margin-bottom","padding-left":"padding-top","padding-right":"padding-bottom",marginRight:"marginBottom"}[e]}getSlideIndex(e){const{slidesEl:t,params:i}=this,r=$n(t,`.${i.slideClass}, swiper-slide`),s=ua(r[0]);return ua(e)-s}getSlideIndexByData(e){return this.getSlideIndex(this.slides.find(t=>t.getAttribute("data-swiper-slide-index")*1===e))}getSlideIndexWhenGrid(e){return this.grid&&this.params.grid&&this.params.grid.rows>1&&(this.params.grid.fill==="column"?e=Math.floor(e/this.params.grid.rows):this.params.grid.fill==="row"&&(e=e%Math.ceil(this.slides.length/this.params.grid.rows))),e}recalcSlides(){const e=this,{slidesEl:t,params:i}=e;e.slides=$n(t,`.${i.slideClass}, swiper-slide`)}enable(){const e=this;e.enabled||(e.enabled=!0,e.params.grabCursor&&e.setGrabCursor(),e.emit("enable"))}disable(){const e=this;e.enabled&&(e.enabled=!1,e.params.grabCursor&&e.unsetGrabCursor(),e.emit("disable"))}setProgress(e,t){const i=this;e=Math.min(Math.max(e,0),1);const r=i.minTranslate(),o=(i.maxTranslate()-r)*e+r;i.translateTo(o,typeof t>"u"?0:t),i.updateActiveIndex(),i.updateSlidesClasses()}emitContainerClasses(){const e=this;if(!e.params._emitClasses||!e.el)return;const t=e.el.className.split(" ").filter(i=>i.indexOf("swiper")===0||i.indexOf(e.params.containerModifierClass)===0);e.emit("_containerClasses",t.join(" "))}getSlideClasses(e){const t=this;return t.destroyed?"":e.className.split(" ").filter(i=>i.indexOf("swiper-slide")===0||i.indexOf(t.params.slideClass)===0).join(" ")}emitSlidesClasses(){const e=this;if(!e.params._emitClasses||!e.el)return;const t=[];e.slides.forEach(i=>{const r=e.getSlideClasses(i);t.push({slideEl:i,classNames:r}),e.emit("_slideClass",i,r)}),e.emit("_slideClasses",t)}slidesPerViewDynamic(e="current",t=!1){const i=this,{params:r,slides:s,slidesGrid:o,slidesSizesGrid:a,size:l,activeIndex:c}=i;let u=1;if(typeof r.slidesPerView=="number")return r.slidesPerView;if(r.centeredSlides){let d=s[c]?Math.ceil(s[c].swiperSlideSize):0,p;for(let f=c+1;f<s.length;f+=1)s[f]&&!p&&(d+=Math.ceil(s[f].swiperSlideSize),u+=1,d>l&&(p=!0));for(let f=c-1;f>=0;f-=1)s[f]&&!p&&(d+=s[f].swiperSlideSize,u+=1,d>l&&(p=!0))}else if(e==="current")for(let d=c+1;d<s.length;d+=1)(t?o[d]+a[d]-o[c]<l:o[d]-o[c]<l)&&(u+=1);else for(let d=c-1;d>=0;d-=1)o[c]-o[d]<l&&(u+=1);return u}update(){const e=this;if(!e||e.destroyed)return;const{snapGrid:t,params:i}=e;i.breakpoints&&e.setBreakpoint(),[...e.el.querySelectorAll('[loading="lazy"]')].forEach(o=>{o.complete&&Zo(e,o)}),e.updateSize(),e.updateSlides(),e.updateProgress(),e.updateSlidesClasses();function r(){const o=e.rtlTranslate?e.translate*-1:e.translate,a=Math.min(Math.max(o,e.maxTranslate()),e.minTranslate());e.setTranslate(a),e.updateActiveIndex(),e.updateSlidesClasses()}let s;if(i.freeMode&&i.freeMode.enabled&&!i.cssMode)r(),i.autoHeight&&e.updateAutoHeight();else{if((i.slidesPerView==="auto"||i.slidesPerView>1)&&e.isEnd&&!i.centeredSlides){const o=e.virtual&&i.virtual.enabled?e.virtual.slides:e.slides;s=e.slideTo(o.length-1,0,!1,!0)}else s=e.slideTo(e.activeIndex,0,!1,!0);s||r()}i.watchOverflow&&t!==e.snapGrid&&e.checkOverflow(),e.emit("update")}changeDirection(e,t=!0){const i=this,r=i.params.direction;return e||(e=r==="horizontal"?"vertical":"horizontal"),e===r||e!=="horizontal"&&e!=="vertical"||(i.el.classList.remove(`${i.params.containerModifierClass}${r}`),i.el.classList.add(`${i.params.containerModifierClass}${e}`),i.emitContainerClasses(),i.params.direction=e,i.slides.forEach(s=>{e==="vertical"?s.style.width="":s.style.height=""}),i.emit("changeDirection"),t&&i.update()),i}changeLanguageDirection(e){const t=this;t.rtl&&e==="rtl"||!t.rtl&&e==="ltr"||(t.rtl=e==="rtl",t.rtlTranslate=t.params.direction==="horizontal"&&t.rtl,t.rtl?(t.el.classList.add(`${t.params.containerModifierClass}rtl`),t.el.dir="rtl"):(t.el.classList.remove(`${t.params.containerModifierClass}rtl`),t.el.dir="ltr"),t.update())}mount(e){const t=this;if(t.mounted)return!0;let i=e||t.params.el;if(typeof i=="string"&&(i=document.querySelector(i)),!i)return!1;i.swiper=t,i.parentNode&&i.parentNode.host&&i.parentNode.host.nodeName===t.params.swiperElementNodeName.toUpperCase()&&(t.isElement=!0);const r=()=>`.${(t.params.wrapperClass||"").trim().split(" ").join(".")}`;let o=i&&i.shadowRoot&&i.shadowRoot.querySelector?i.shadowRoot.querySelector(r()):$n(i,r())[0];return!o&&t.params.createElements&&(o=ca("div",t.params.wrapperClass),i.append(o),$n(i,`.${t.params.slideClass}`).forEach(a=>{o.append(a)})),Object.assign(t,{el:i,wrapperEl:o,slidesEl:t.isElement&&!i.parentNode.host.slideSlots?i.parentNode.host:o,hostEl:t.isElement?i.parentNode.host:i,mounted:!0,rtl:i.dir.toLowerCase()==="rtl"||Ri(i,"direction")==="rtl",rtlTranslate:t.params.direction==="horizontal"&&(i.dir.toLowerCase()==="rtl"||Ri(i,"direction")==="rtl"),wrongRTL:Ri(o,"display")==="-webkit-box"}),!0}init(e){const t=this;if(t.initialized||t.mount(e)===!1)return t;t.emit("beforeInit"),t.params.breakpoints&&t.setBreakpoint(),t.addClasses(),t.updateSize(),t.updateSlides(),t.params.watchOverflow&&t.checkOverflow(),t.params.grabCursor&&t.enabled&&t.setGrabCursor(),t.params.loop&&t.virtual&&t.params.virtual.enabled?t.slideTo(t.params.initialSlide+t.virtual.slidesBefore,0,t.params.runCallbacksOnInit,!1,!0):t.slideTo(t.params.initialSlide,0,t.params.runCallbacksOnInit,!1,!0),t.params.loop&&t.loopCreate(void 0,!0),t.attachEvents();const r=[...t.el.querySelectorAll('[loading="lazy"]')];return t.isElement&&r.push(...t.hostEl.querySelectorAll('[loading="lazy"]')),r.forEach(s=>{s.complete?Zo(t,s):s.addEventListener("load",o=>{Zo(t,o.target)})}),Ql(t),t.initialized=!0,Ql(t),t.emit("init"),t.emit("afterInit"),t}destroy(e=!0,t=!0){const i=this,{params:r,el:s,wrapperEl:o,slides:a}=i;return typeof i.params>"u"||i.destroyed||(i.emit("beforeDestroy"),i.initialized=!1,i.detachEvents(),r.loop&&i.loopDestroy(),t&&(i.removeClasses(),s&&typeof s!="string"&&s.removeAttribute("style"),o&&o.removeAttribute("style"),a&&a.length&&a.forEach(l=>{l.classList.remove(r.slideVisibleClass,r.slideFullyVisibleClass,r.slideActiveClass,r.slideNextClass,r.slidePrevClass),l.removeAttribute("style"),l.removeAttribute("data-swiper-slide-index")})),i.emit("destroy"),Object.keys(i.eventsListeners).forEach(l=>{i.off(l)}),e!==!1&&(i.el&&typeof i.el!="string"&&(i.el.swiper=null),Mg(i)),i.destroyed=!0),null}static extendDefaults(e){hn(tl,e)}static get extendedDefaults(){return tl}static get defaults(){return Rd}static installModule(e){Tn.prototype.__modules__||(Tn.prototype.__modules__=[]);const t=Tn.prototype.__modules__;typeof e=="function"&&t.indexOf(e)<0&&t.push(e)}static use(e){return Array.isArray(e)?(e.forEach(t=>Tn.installModule(t)),Tn):(Tn.installModule(e),Tn)}}Object.keys(el).forEach(n=>{Object.keys(el[n]).forEach(e=>{Tn.prototype[e]=el[n][e]})});Tn.use([Fg,Ng]);function Ef(n,e,t,i){return n.params.createElements&&Object.keys(i).forEach(r=>{if(!t[r]&&t.auto===!0){let s=$n(n.el,`.${i[r]}`)[0];s||(s=ca("div",i[r]),s.className=i[r],n.el.append(s)),t[r]=s,e[r]=s}}),t}const H_='<svg class="swiper-navigation-icon" width="11" height="20" viewBox="0 0 11 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M0.38296 20.0762C0.111788 19.805 0.111788 19.3654 0.38296 19.0942L9.19758 10.2796L0.38296 1.46497C0.111788 1.19379 0.111788 0.754138 0.38296 0.482966C0.654131 0.211794 1.09379 0.211794 1.36496 0.482966L10.4341 9.55214C10.8359 9.9539 10.8359 10.6053 10.4341 11.007L1.36496 20.0762C1.09379 20.3474 0.654131 20.3474 0.38296 20.0762Z" fill="currentColor"/></svg>';function G_({swiper:n,extendParams:e,on:t,emit:i}){e({navigation:{nextEl:null,prevEl:null,addIcons:!0,hideOnClick:!1,disabledClass:"swiper-button-disabled",hiddenClass:"swiper-button-hidden",lockClass:"swiper-button-lock",navigationDisabledClass:"swiper-navigation-disabled"}}),n.navigation={nextEl:null,prevEl:null};function r(f){let _;return f&&typeof f=="string"&&n.isElement&&(_=n.el.querySelector(f)||n.hostEl.querySelector(f),_)?_:(f&&(typeof f=="string"&&(_=[...document.querySelectorAll(f)]),n.params.uniqueNavElements&&typeof f=="string"&&_&&_.length>1&&n.el.querySelectorAll(f).length===1?_=n.el.querySelector(f):_&&_.length===1&&(_=_[0])),f&&!_?f:_)}function s(f,_){const g=n.params.navigation;f=It(f),f.forEach(m=>{m&&(m.classList[_?"add":"remove"](...g.disabledClass.split(" ")),m.tagName==="BUTTON"&&(m.disabled=_),n.params.watchOverflow&&n.enabled&&m.classList[n.isLocked?"add":"remove"](g.lockClass))})}function o(){const{nextEl:f,prevEl:_}=n.navigation;if(n.params.loop){s(_,!1),s(f,!1);return}s(_,n.isBeginning&&!n.params.rewind),s(f,n.isEnd&&!n.params.rewind)}function a(f){f.preventDefault(),!(n.isBeginning&&!n.params.loop&&!n.params.rewind)&&(n.slidePrev(),i("navigationPrev"))}function l(f){f.preventDefault(),!(n.isEnd&&!n.params.loop&&!n.params.rewind)&&(n.slideNext(),i("navigationNext"))}function c(){const f=n.params.navigation;if(n.params.navigation=Ef(n,n.originalParams.navigation,n.params.navigation,{nextEl:"swiper-button-next",prevEl:"swiper-button-prev"}),!(f.nextEl||f.prevEl))return;let _=r(f.nextEl),g=r(f.prevEl);Object.assign(n.navigation,{nextEl:_,prevEl:g}),_=It(_),g=It(g);const m=(h,v)=>{if(h){if(f.addIcons&&h.matches(".swiper-button-next,.swiper-button-prev")&&!h.querySelector("svg")){const x=document.createElement("div");Jl(x,H_),h.appendChild(x.querySelector("svg")),x.remove()}h.addEventListener("click",v==="next"?l:a)}!n.enabled&&h&&h.classList.add(...f.lockClass.split(" "))};_.forEach(h=>m(h,"next")),g.forEach(h=>m(h,"prev"))}function u(){let{nextEl:f,prevEl:_}=n.navigation;f=It(f),_=It(_);const g=(m,h)=>{m.removeEventListener("click",h==="next"?l:a),m.classList.remove(...n.params.navigation.disabledClass.split(" "))};f.forEach(m=>g(m,"next")),_.forEach(m=>g(m,"prev"))}t("init",()=>{n.params.navigation.enabled===!1?p():(c(),o())}),t("toEdge fromEdge lock unlock",()=>{o()}),t("destroy",()=>{u()}),t("enable disable",()=>{let{nextEl:f,prevEl:_}=n.navigation;if(f=It(f),_=It(_),n.enabled){o();return}[...f,..._].filter(g=>!!g).forEach(g=>g.classList.add(n.params.navigation.lockClass))}),t("click",(f,_)=>{let{nextEl:g,prevEl:m}=n.navigation;g=It(g),m=It(m);const h=_.target;let v=m.includes(h)||g.includes(h);if(n.isElement&&!v){const x=_.path||_.composedPath&&_.composedPath();x&&(v=x.find(w=>g.includes(w)||m.includes(w)))}if(n.params.navigation.hideOnClick&&!v){if(n.pagination&&n.params.pagination&&n.params.pagination.clickable&&(n.pagination.el===h||n.pagination.el.contains(h)))return;let x;g.length?x=g[0].classList.contains(n.params.navigation.hiddenClass):m.length&&(x=m[0].classList.contains(n.params.navigation.hiddenClass)),i(x===!0?"navigationShow":"navigationHide"),[...g,...m].filter(w=>!!w).forEach(w=>w.classList.toggle(n.params.navigation.hiddenClass))}});const d=()=>{n.el.classList.remove(...n.params.navigation.navigationDisabledClass.split(" ")),c(),o()},p=()=>{n.el.classList.add(...n.params.navigation.navigationDisabledClass.split(" ")),u()};Object.assign(n.navigation,{enable:d,disable:p,update:o,init:c,destroy:u})}function Ts(n=""){return`.${n.trim().replace(/([\.:!+\/()[\]])/g,"\\$1").replace(/ /g,".")}`}function W_({swiper:n,extendParams:e,on:t,emit:i}){const r="swiper-pagination";e({pagination:{el:null,bulletElement:"span",clickable:!1,hideOnClick:!1,renderBullet:null,renderProgressbar:null,renderFraction:null,renderCustom:null,progressbarOpposite:!1,type:"bullets",dynamicBullets:!1,dynamicMainBullets:1,formatFractionCurrent:h=>h,formatFractionTotal:h=>h,bulletClass:`${r}-bullet`,bulletActiveClass:`${r}-bullet-active`,modifierClass:`${r}-`,currentClass:`${r}-current`,totalClass:`${r}-total`,hiddenClass:`${r}-hidden`,progressbarFillClass:`${r}-progressbar-fill`,progressbarOppositeClass:`${r}-progressbar-opposite`,clickableClass:`${r}-clickable`,lockClass:`${r}-lock`,horizontalClass:`${r}-horizontal`,verticalClass:`${r}-vertical`,paginationDisabledClass:`${r}-disabled`}}),n.pagination={el:null,bullets:[]};let s,o=0;function a(){return!n.params.pagination.el||!n.pagination.el||Array.isArray(n.pagination.el)&&n.pagination.el.length===0}function l(h,v){const{bulletActiveClass:x}=n.params.pagination;h&&(h=h[`${v==="prev"?"previous":"next"}ElementSibling`],h&&(h.classList.add(`${x}-${v}`),h=h[`${v==="prev"?"previous":"next"}ElementSibling`],h&&h.classList.add(`${x}-${v}-${v}`)))}function c(h,v,x){if(h=h%x,v=v%x,v===h+1)return"next";if(v===h-1)return"previous"}function u(h){const v=h.target.closest(Ts(n.params.pagination.bulletClass));if(!v)return;h.preventDefault();const x=ua(v)*n.params.slidesPerGroup;if(n.params.loop){if(n.realIndex===x)return;const w=c(n.realIndex,x,n.slides.length);w==="next"?n.slideNext():w==="previous"?n.slidePrev():n.slideToLoop(x)}else n.slideTo(x)}function d(){const h=n.rtl,v=n.params.pagination;if(a())return;let x=n.pagination.el;x=It(x);let w,S;const C=n.virtual&&n.params.virtual.enabled?n.virtual.slides.length:n.slides.length,T=n.params.loop?Math.ceil(C/n.params.slidesPerGroup):n.snapGrid.length;if(n.params.loop?(S=n.previousRealIndex||0,w=n.params.slidesPerGroup>1?Math.floor(n.realIndex/n.params.slidesPerGroup):n.realIndex):typeof n.snapIndex<"u"?(w=n.snapIndex,S=n.previousSnapIndex):(S=n.previousIndex||0,w=n.activeIndex||0),v.type==="bullets"&&n.pagination.bullets&&n.pagination.bullets.length>0){const A=n.pagination.bullets;let b,y,P;if(v.dynamicBullets&&(s=Zl(A[0],n.isHorizontal()?"width":"height"),x.forEach(D=>{D.style[n.isHorizontal()?"width":"height"]=`${s*(v.dynamicMainBullets+4)}px`}),v.dynamicMainBullets>1&&S!==void 0&&(o+=w-(S||0),o>v.dynamicMainBullets-1?o=v.dynamicMainBullets-1:o<0&&(o=0)),b=Math.max(w-o,0),y=b+(Math.min(A.length,v.dynamicMainBullets)-1),P=(y+b)/2),A.forEach(D=>{const O=[...["","-next","-next-next","-prev","-prev-prev","-main"].map(V=>`${v.bulletActiveClass}${V}`)].map(V=>typeof V=="string"&&V.includes(" ")?V.split(" "):V).flat();D.classList.remove(...O)}),x.length>1)A.forEach(D=>{const O=ua(D);O===w?D.classList.add(...v.bulletActiveClass.split(" ")):n.isElement&&D.setAttribute("part","bullet"),v.dynamicBullets&&(O>=b&&O<=y&&D.classList.add(...`${v.bulletActiveClass}-main`.split(" ")),O===b&&l(D,"prev"),O===y&&l(D,"next"))});else{const D=A[w];if(D&&D.classList.add(...v.bulletActiveClass.split(" ")),n.isElement&&A.forEach((O,V)=>{O.setAttribute("part",V===w?"bullet-active":"bullet")}),v.dynamicBullets){const O=A[b],V=A[y];for(let k=b;k<=y;k+=1)A[k]&&A[k].classList.add(...`${v.bulletActiveClass}-main`.split(" "));l(O,"prev"),l(V,"next")}}if(v.dynamicBullets){const D=Math.min(A.length,v.dynamicMainBullets+4),O=(s*D-s)/2-P*s,V=h?"right":"left";A.forEach(k=>{k.style[n.isHorizontal()?V:"top"]=`${O}px`})}}x.forEach((A,b)=>{if(v.type==="fraction"&&(A.querySelectorAll(Ts(v.currentClass)).forEach(y=>{y.textContent=v.formatFractionCurrent(w+1)}),A.querySelectorAll(Ts(v.totalClass)).forEach(y=>{y.textContent=v.formatFractionTotal(T)})),v.type==="progressbar"){let y;v.progressbarOpposite?y=n.isHorizontal()?"vertical":"horizontal":y=n.isHorizontal()?"horizontal":"vertical";const P=(w+1)/T;let D=1,O=1;y==="horizontal"?D=P:O=P,A.querySelectorAll(Ts(v.progressbarFillClass)).forEach(V=>{V.style.transform=`translate3d(0,0,0) scaleX(${D}) scaleY(${O})`,V.style.transitionDuration=`${n.params.speed}ms`})}v.type==="custom"&&v.renderCustom?(Jl(A,v.renderCustom(n,w+1,T)),b===0&&i("paginationRender",A)):(b===0&&i("paginationRender",A),i("paginationUpdate",A)),n.params.watchOverflow&&n.enabled&&A.classList[n.isLocked?"add":"remove"](v.lockClass)})}function p(){const h=n.params.pagination;if(a())return;const v=n.virtual&&n.params.virtual.enabled?n.virtual.slides.length:n.grid&&n.params.grid.rows>1?n.slides.length/Math.ceil(n.params.grid.rows):n.slides.length;let x=n.pagination.el;x=It(x);let w="";if(h.type==="bullets"){let S=n.params.loop?Math.ceil(v/n.params.slidesPerGroup):n.snapGrid.length;n.params.freeMode&&n.params.freeMode.enabled&&S>v&&(S=v);for(let C=0;C<S;C+=1)h.renderBullet?w+=h.renderBullet.call(n,C,h.bulletClass):w+=`<${h.bulletElement} ${n.isElement?'part="bullet"':""} class="${h.bulletClass}"></${h.bulletElement}>`}h.type==="fraction"&&(h.renderFraction?w=h.renderFraction.call(n,h.currentClass,h.totalClass):w=`<span class="${h.currentClass}"></span> / <span class="${h.totalClass}"></span>`),h.type==="progressbar"&&(h.renderProgressbar?w=h.renderProgressbar.call(n,h.progressbarFillClass):w=`<span class="${h.progressbarFillClass}"></span>`),n.pagination.bullets=[],x.forEach(S=>{h.type!=="custom"&&Jl(S,w||""),h.type==="bullets"&&n.pagination.bullets.push(...S.querySelectorAll(Ts(h.bulletClass)))}),h.type!=="custom"&&i("paginationRender",x[0])}function f(){n.params.pagination=Ef(n,n.originalParams.pagination,n.params.pagination,{el:"swiper-pagination"});const h=n.params.pagination;if(!h.el)return;let v;typeof h.el=="string"&&n.isElement&&(v=n.el.querySelector(h.el)),!v&&typeof h.el=="string"&&(v=[...document.querySelectorAll(h.el)]),v||(v=h.el),!(!v||v.length===0)&&(n.params.uniqueNavElements&&typeof h.el=="string"&&Array.isArray(v)&&v.length>1&&(v=[...n.el.querySelectorAll(h.el)],v.length>1&&(v=v.find(x=>vf(x,".swiper")[0]===n.el))),Array.isArray(v)&&v.length===1&&(v=v[0]),Object.assign(n.pagination,{el:v}),v=It(v),v.forEach(x=>{h.type==="bullets"&&h.clickable&&x.classList.add(...(h.clickableClass||"").split(" ")),x.classList.add(h.modifierClass+h.type),x.classList.add(n.isHorizontal()?h.horizontalClass:h.verticalClass),h.type==="bullets"&&h.dynamicBullets&&(x.classList.add(`${h.modifierClass}${h.type}-dynamic`),o=0,h.dynamicMainBullets<1&&(h.dynamicMainBullets=1)),h.type==="progressbar"&&h.progressbarOpposite&&x.classList.add(h.progressbarOppositeClass),h.clickable&&x.addEventListener("click",u),n.enabled||x.classList.add(h.lockClass)}))}function _(){const h=n.params.pagination;if(a())return;let v=n.pagination.el;v&&(v=It(v),v.forEach(x=>{x.classList.remove(h.hiddenClass),x.classList.remove(h.modifierClass+h.type),x.classList.remove(n.isHorizontal()?h.horizontalClass:h.verticalClass),h.clickable&&(x.classList.remove(...(h.clickableClass||"").split(" ")),x.removeEventListener("click",u))})),n.pagination.bullets&&n.pagination.bullets.forEach(x=>x.classList.remove(...h.bulletActiveClass.split(" ")))}t("changeDirection",()=>{if(!n.pagination||!n.pagination.el)return;const h=n.params.pagination;let{el:v}=n.pagination;v=It(v),v.forEach(x=>{x.classList.remove(h.horizontalClass,h.verticalClass),x.classList.add(n.isHorizontal()?h.horizontalClass:h.verticalClass)})}),t("init",()=>{n.params.pagination.enabled===!1?m():(f(),p(),d())}),t("activeIndexChange",()=>{typeof n.snapIndex>"u"&&d()}),t("snapIndexChange",()=>{d()}),t("snapGridLengthChange",()=>{p(),d()}),t("destroy",()=>{_()}),t("enable disable",()=>{let{el:h}=n.pagination;h&&(h=It(h),h.forEach(v=>v.classList[n.enabled?"remove":"add"](n.params.pagination.lockClass)))}),t("lock unlock",()=>{d()}),t("click",(h,v)=>{const x=v.target,w=It(n.pagination.el);if(n.params.pagination.el&&n.params.pagination.hideOnClick&&w&&w.length>0&&!x.classList.contains(n.params.pagination.bulletClass)){if(n.navigation&&(n.navigation.nextEl&&x===n.navigation.nextEl||n.navigation.prevEl&&x===n.navigation.prevEl))return;const S=w[0].classList.contains(n.params.pagination.hiddenClass);i(S===!0?"paginationShow":"paginationHide"),w.forEach(C=>C.classList.toggle(n.params.pagination.hiddenClass))}});const g=()=>{n.el.classList.remove(n.params.pagination.paginationDisabledClass);let{el:h}=n.pagination;h&&(h=It(h),h.forEach(v=>v.classList.remove(n.params.pagination.paginationDisabledClass))),f(),p(),d()},m=()=>{n.el.classList.add(n.params.pagination.paginationDisabledClass);let{el:h}=n.pagination;h&&(h=It(h),h.forEach(v=>v.classList.add(n.params.pagination.paginationDisabledClass))),_()};Object.assign(n.pagination,{enable:g,disable:m,render:p,update:d,init:f,destroy:_})}class X_{#e;#t=new Set;constructor(e){this.#e=e}get current(){return this.#e}set current(e){this.#e!=e&&(this.#e=e,this.#t.forEach(t=>t(e)))}on(e){return this.#t.add(e),()=>this.#t.delete(e)}}const Mf=n=>new X_(n),ec=Symbol.for("atomico.hooks");globalThis[ec]=globalThis[ec]||{};let ns=globalThis[ec];const $_=Symbol.for("Atomico.suspense"),Tf=Symbol.for("Atomico.effect"),q_=Symbol.for("Atomico.layoutEffect"),Af=Symbol.for("Atomico.insertionEffect"),gs=(n,e,t)=>{const{i,hooks:r}=ns.c,s=r[i]=r[i]||{};return s.value=n(s.value),s.effect=e,s.tag=t,ns.c.i++,r[i].value},Y_=n=>gs((e=Mf(n))=>e),ao=()=>gs((n=Mf(ns.c.host))=>n),Cf=()=>ns.c.update,j_=(n,e,t=0)=>{let i={},r=!1;const s=()=>r,o=(a,l)=>{for(const c in i){const u=i[c];u.effect&&u.tag===a&&(u.value=u.effect(u.value,l))}};return{load:a=>{ns.c={host:e,hooks:i,update:n,i:0,id:t};let l;try{r=!1,l=a()}catch(c){if(c!==$_)throw c;r=!0}finally{ns.c=null}return l},cleanEffects:a=>(o(Af,a),()=>(o(q_,a),()=>{o(Tf,a)})),isSuspense:s}},_s=Symbol.for;function Pf(n,e){const t=n.length;if(t!==e.length)return!1;for(let i=0;i<t;i++){let r=n[i],s=e[i];if(r!==s)return!1}return!0}const Wn=n=>typeof n=="function",Os=n=>typeof n=="object",{isArray:K_}=Array,tc=(n,e)=>(e?n instanceof HTMLStyleElement:!0)&&"hydrate"in(n?.dataset||{});function Rf(n,e){let t;const i=r=>{let{length:s}=r;for(let o=0;o<s;o++){const a=r[o];if(a&&Array.isArray(a))i(a);else{const l=typeof a;if(a==null||l==="function"||l==="boolean")continue;l==="string"||l==="number"?(t==null&&(t=""),t+=a):(t!=null&&(e(t),t=null),e(a))}}};i(n),t!=null&&e(t)}const Df=(n,e,t)=>(n.addEventListener(e,t),()=>n.removeEventListener(e,t));class Lf{constructor(e,t,i){this.message=t,this.target=e,this.value=i}}class If extends Lf{}class Z_ extends Lf{}const da="Custom",J_=null,Q_={true:1,"":1,1:1};function ev(n,e,t,i,r){const{type:s,reflect:o,event:a,value:l,attr:c=tv(e)}=t?.name!=da&&Os(t)&&t!=J_?t:{type:t},u=s?.name===da&&s.map,d=l!=null?s==Function||!Wn(l)?()=>l:l:null;Object.defineProperty(n,e,{configurable:!0,set(p){const f=this[e];d&&s!=Boolean&&p==null&&(p=d());const{error:_,value:g}=(u?rv:sv)(s,p);if(_&&g!=null)throw new If(this,`The value defined for prop '${e}' must be of type '${s.name}'`,g);f!=g&&(this._props[e]=g??void 0,this.update(),a&&Uf(this,a),this.updated.then(()=>{o&&(this._ignoreAttr=c,nv(this,s,c,this[e]),this._ignoreAttr=null)}))},get(){return this._props[e]}}),d&&(r[e]=d()),i[c]={prop:e,type:s}}const Uf=(n,{type:e,base:t=CustomEvent,...i})=>n.dispatchEvent(new t(e,i)),tv=n=>n.replace(/([A-Z])/g,"-$1").toLowerCase(),nv=(n,e,t,i)=>i==null||e==Boolean&&!i?n.removeAttribute(t):n.setAttribute(t,e?.name===da&&e?.serialize?e?.serialize(i):Os(i)?JSON.stringify(i):e==Boolean?"":i),iv=(n,e)=>n==Boolean?!!Q_[e]:n==Number?Number(e):n==String?e:n==Array||n==Object?JSON.parse(e):n.name==da?e:new n(e),rv=({map:n},e)=>{try{return{value:n(e),error:!1}}catch{return{value:e,error:!0}}},sv=(n,e)=>n==null||e==null?{value:e,error:!1}:n!=String&&e===""?{value:void 0,error:!1}:n==Object||n==Array||n==Symbol?{value:e,error:{}.toString.call(e)!==`[object ${n.name}]`}:e instanceof n?{value:e,error:n==Number&&Number.isNaN(e.valueOf())}:n==String||n==Number||n==Boolean?{value:e,error:n==Number?typeof e!="number"?!0:Number.isNaN(e):n==String?typeof e!="string":typeof e!="boolean"}:{value:e,error:!0};let ov=0;const av=n=>(n?.dataset||{})?.hydrate||""||"c"+ov++,lo=(n,e=HTMLElement)=>{const t={},i={},r="prototype"in e&&e.prototype instanceof Element,s=r?e:"base"in e?e.base:HTMLElement,{props:o,styles:a}=r?n:e;class l extends s{constructor(){super(),this._setup(),this._render=()=>n({...this._props});for(const u in i)this[u]=i[u]}static get styles(){return[super.styles,a]}async _setup(){if(this._props)return;this._props={};let u,d;this.mounted=new Promise(m=>this.mount=()=>{m(),u!=this.parentNode&&(d!=u?this.unmounted.then(this.update):this.update()),u=this.parentNode}),this.unmounted=new Promise(m=>this.unmount=()=>{m(),(u!=this.parentNode||!this.isConnected)&&(p.cleanEffects(!0)()(),d=this.parentNode,u=null)}),this.symbolId=this.symbolId||Symbol(),this.symbolIdParent=Symbol();const p=j_(()=>this.update(),this,av(this));let f,_=!0;const g=tc(this);this.update=()=>(f||(f=!0,this.updated=(this.updated||this.mounted).then(()=>{try{const m=p.load(this._render),h=p.cleanEffects();return m&&m.render(this,this.symbolId,g),f=!1,_&&!p.isSuspense()&&(_=!1,!g&&lv(this)),h()}finally{f=!1}}).then(m=>{m&&m()})),this.updated),this.update()}connectedCallback(){this.mount(),super.connectedCallback&&super.connectedCallback()}disconnectedCallback(){super.disconnectedCallback&&super.disconnectedCallback(),this.unmount()}attributeChangedCallback(u,d,p){if(t[u]){if(u===this._ignoreAttr||d===p)return;const{prop:f,type:_}=t[u];try{this[f]=iv(_,p)}catch{throw new Z_(this,`The value defined as attr '${u}' cannot be parsed by type '${_.name}'`,p)}}else super.attributeChangedCallback(u,d,p)}static get props(){return{...super.props,...o}}static get observedAttributes(){const u=super.observedAttributes||[];for(const d in o)ev(this.prototype,d,o[d],t,i);return Object.keys(t).concat(u)}}return l};function lv(n){const{styles:e}=n.constructor,{shadowRoot:t}=n;if(t&&e.length){const i=[];Rf(e,r=>{r&&(r instanceof Element?t.appendChild(r.cloneNode(!0)):i.push(r))}),i.length&&(t.adoptedStyleSheets=i)}}const Of=n=>(e,t)=>{gs(([i,r]=[])=>((r||!r)&&(r&&Pf(r,t)?i=i||!0:(Wn(i)&&i(),i=null)),[i,t]),([i,r],s)=>s?(Wn(i)&&i(),[]):[i||e(),r],n)},Gs=Of(Tf),cv=Of(Af);class Ff extends Array{constructor(e,t){let i=!0;const r=s=>{try{t(s,this,i)}finally{i=!1}};super(void 0,r,t),r(e)}}const _u=n=>{const e=Cf();return gs((t=new Ff(n,(i,r,s)=>{i=Wn(i)?i(r[0]):i,i!==r[0]&&(r[0]=i,s||e())}))=>t)},pi=(n,e)=>{const[t]=gs(([i,r,s=0]=[])=>((!r||r&&!Pf(r,e))&&(i=n()),[i,e,s]));return t},vu=n=>{const{current:e}=ao();if(!(n in e))throw new If(e,`For useProp("${n}"), the prop does not exist on the host.`,n);return gs((t=new Ff(e[n],(i,r)=>{i=Wn(i)?i(e[n]):i,e[n]=i}))=>(t[0]=e[n],t))},Fi=(n,e={})=>{const t=ao();return t[n]||(t[n]=(i=e.detail)=>Uf(t.current,{type:n,...e,detail:i})),t[n]},nc=_s("atomico/options");globalThis[nc]=globalThis[nc]||{sheet:!!document.adoptedStyleSheets};const Nf=globalThis[nc],uv={checked:1,value:1,selected:1},dv={list:1,type:1,size:1,form:1,width:1,height:1,src:1,href:1,slot:1},hv={shadowDom:1,staticNode:1,cloneNode:1,children:1,key:1},Jo={},ic=[];class rc extends Text{}const fv=_s("atomico/id"),Fs=_s("atomico/type"),nl=_s("atomico/ref"),kf=_s("atomico/vnode"),pv=()=>{};function mv(n,e,t){return zf(this,n,e,t)}const Bf=(n,e,...t)=>{const i=e||Jo;let{children:r}=i;if(r=r??(t.length?t:ic),n===pv)return r;const s=n?n instanceof Node?1:n.prototype instanceof HTMLElement&&2:0;if(s===!1&&n instanceof Function)return n(r!=ic?{children:r,...i}:i);const o=Nf.render||mv;return{[Fs]:kf,type:n,props:i,children:r,key:i.key,shadow:i.shadowDom,static:i.staticNode,raw:s,is:i.is,clone:i.cloneNode,render:o}};function zf(n,e,t=fv,i,r){let s;if(e&&e[t]&&e[t].vnode==n||n[Fs]!=kf)return e;(n||!e)&&(r=r||n.type=="svg",s=n.type!="host"&&(n.raw==1?(e&&n.clone?e[nl]:e)!=n.type:n.raw==2?!(e instanceof n.type):e?e[nl]||e.localName!=n.type:!e),s&&n.type!=null&&(n.raw==1&&n.clone?(i=!0,e=n.type.cloneNode(!0),e[nl]=n.type):e=n.raw==1?n.type:n.raw==2?new n.type:r?document.createElementNS("http://www.w3.org/2000/svg",n.type):document.createElement(n.type,n.is?{is:n.is}:void 0)));const o=e[t]?e[t]:Jo,{vnode:a=Jo,cycle:l=0}=o;let{fragment:c,handlers:u}=o;const{children:d=ic,props:p=Jo}=a;if(u=s?{}:u||{},n.static&&!s)return e;if(n.shadow&&!e.shadowRoot&&e.attachShadow({mode:"open",...n.shadow}),n.props!=p&&vv(e,p,n.props,u,r),n.children!==d){const f=n.shadow?e.shadowRoot:e;c=_v(n.children,c,f,t,!l&&i,r&&n.type=="foreignObject"?!1:r)}return e[t]={vnode:n,handlers:u,fragment:c,cycle:l+1},e}function gv(n,e){const t=new rc(""),i=new rc("");let r;if(n[e?"prepend":"append"](t),e){let{lastElementChild:s}=n;for(;s;){const{previousElementSibling:o}=s;if(tc(s,!0)&&!tc(o,!0)){r=s;break}s=o}}return r?r.before(i):n.append(i),{markStart:t,markEnd:i}}function _v(n,e,t,i,r,s){n=n==null?null:K_(n)?n:[n];const o=e||gv(t,r),{markStart:a,markEnd:l,keyes:c}=o;let u;const d=c&&new Set;let p=a;if(n&&Rf(n,f=>{if(typeof f=="object"&&!f[Fs])return;const _=f[Fs]&&f.key,g=c&&_!=null&&c.get(_);p!=l&&p===g?d.delete(p):p=p==l?l:p.nextSibling;const m=c?g:p;let h=m;if(f[Fs])h=zf(f,m,i,r,s);else{const v=f+"";!(h instanceof Text)||h instanceof rc?h=new Text(v):h.data!=v&&(h.data=v)}h!=p&&(c&&d.delete(h),!m||c?(t.insertBefore(h,p),c&&p!=l&&d.add(p)):m==l?t.insertBefore(h,l):(t.replaceChild(h,m),p=h)),_!=null&&(u=u||new Map,u.set(_,h))}),p=p==l?l:p.nextSibling,e&&p!=l)for(;p!=l;){const f=p;p=p.nextSibling,f.remove()}return d&&d.forEach(f=>f.remove()),o.keyes=u,o}function vv(n,e,t,i,r){for(const s in e)!(s in t)&&Dd(n,s,e[s],null,r,i);for(const s in t)Dd(n,s,e[s],t[s],r,i)}function Dd(n,e,t,i,r,s){if(e=e=="class"&&!r?"className":e,t=t??null,i=i??null,e in n&&uv[e]&&(t=n[e]),!(i===t||hv[e]||e[0]=="_"))if(e[0]=="o"&&e[1]=="n"&&(Wn(i)||Wn(t)))xv(n,e.slice(2),i,s);else if(e=="ref")i&&(Wn(i)?i(n):i.current=n);else if(e=="style"){const{style:o}=n;t=t||"",i=i||"";const a=Os(t),l=Os(i);if(a)for(const c in t)if(l)!(c in i)&&Ld(o,c,null);else break;if(l)for(const c in i){const u=i[c];a&&t[c]===u||Ld(o,c,u)}else o.cssText=i}else{const o=e[0]=="$"?e.slice(1):e;o===e&&(!r&&!dv[e]&&e in n||Wn(i)||Wn(t))?n[e]=i??"":i==null?n.removeAttribute(o):n.setAttribute(o,Os(i)?JSON.stringify(i):i)}}function xv(n,e,t,i){if(i.handleEvent||(i.handleEvent=r=>i[r.type].call(n,r)),t){if(!i[e]){const r=t.capture||t.once||t.passive?Object.assign({},t):null;n.addEventListener(e,i,r)}i[e]=t}else i[e]&&(n.removeEventListener(e,i),delete i[e])}function Ld(n,e,t){let i="setProperty";t==null&&(i="removeProperty",t=null),~e.indexOf("-")?n[i](e,t):n[e]=t}const Id={};function Da(n,...e){const t=(n.raw||n).reduce((i,r,s)=>i+r+(e[s]||""),"");return Id[t]=Id[t]||wv(t)}function wv(n){if(Nf.sheet){const e=new CSSStyleSheet;return e.replaceSync(n),e}else{const e=document.createElement("style");return e.textContent=n,e}}const yv=Bf("host",{style:"display: contents"}),il=_s("atomico/context"),bv=(n,e)=>{const t=ao();cv(()=>Df(t.current,"ConnectContext",i=>{n===i.detail.id&&(i.stopPropagation(),i.detail.connect(e))}),[n])},Sv=n=>{const e=Fi("ConnectContext",{bubbles:!0,composed:!0}),t=()=>{let s;return e({id:n,connect(o){s=o}}),s},[i,r]=_u(t);return Gs(()=>{i||(n[il]||(n[il]=customElements.whenDefined(new n().localName)),n[il].then(()=>r(t)))},[n]),i},Ev=n=>{const e=Sv(n),t=Cf();return Gs(()=>{if(e)return Df(e,"UpdatedValue",t)},[e]),(e||n).value},Mv=n=>{const e=lo(()=>(bv(e,ao().current),yv),{props:{value:{type:Object,event:{type:"UpdatedValue"},value:()=>n}}});return e.value=n,e},lt=(n,e,t)=>(e==null?e={key:t}:e.key=t,Bf(n,e)),Ns=lt,Vf=Da`*,*:before,*:after{box-sizing:border-box}button{padding:0;touch-action:manipulation;cursor:pointer;user-select:none}`,Hf=Da`.vh{position:absolute;transform:scale(0)}`;function xu(){const n=new Date;return new Ct(n.getFullYear(),n.getMonth()+1,n.getDate())}function wu(n,e=0){const t=Bn(n),i=t.getUTCDay(),r=(i<e?7:0)+i-e;return t.setUTCDate(t.getUTCDate()-r),Ct.from(t)}function Gf(n,e=0){return wu(n,e).add({days:6})}function Wf(n){return Ct.from(new Date(Date.UTC(n.year,n.month,0)))}function La(n,e,t){return e&&Ct.compare(n,e)<0?e:t&&Ct.compare(n,t)>0?t:n}const Tv={days:1};function Av(n,e=0){let t=wu(n.toPlainDate(),e);const i=Gf(Wf(n),e),r=[];for(;Ct.compare(t,i)<0;){const s=[];for(let o=0;o<7;o++)s.push(t),t=t.add(Tv);r.push(s)}return r}function Bn(n){return new Date(Date.UTC(n.year,n.month-1,n.day??1))}const Cv=/^(\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[0-1])$/,rl=(n,e)=>n.toString().padStart(e,"0");class Ct{constructor(e,t,i){this.year=e,this.month=t,this.day=i}add(e){const t=Bn(this);if("days"in e)return t.setUTCDate(this.day+e.days),Ct.from(t);let{year:i,month:r}=this;"months"in e?(r=this.month+e.months,t.setUTCMonth(r-1)):(i=this.year+e.years,t.setUTCFullYear(i));const s=Ct.from(Bn({year:i,month:r,day:1}));return La(Ct.from(t),s,Wf(s))}toString(){return`${rl(this.year,4)}-${rl(this.month,2)}-${rl(this.day,2)}`}toPlainYearMonth(){return new Ia(this.year,this.month)}equals(e){return Ct.compare(this,e)===0}static compare(e,t){return e.year<t.year?-1:e.year>t.year?1:e.month<t.month?-1:e.month>t.month?1:e.day<t.day?-1:e.day>t.day?1:0}static from(e){if(typeof e=="string"){const t=e.match(Cv);if(!t)throw new TypeError(e);const[,i,r,s]=t;return new Ct(parseInt(i,10),parseInt(r,10),parseInt(s,10))}return new Ct(e.getUTCFullYear(),e.getUTCMonth()+1,e.getUTCDate())}}class Ia{constructor(e,t){this.year=e,this.month=t}add(e){const t=Bn(this),i=(e.months??0)+(e.years??0)*12;return t.setUTCMonth(t.getUTCMonth()+i),new Ia(t.getUTCFullYear(),t.getUTCMonth()+1)}equals(e){return this.year===e.year&&this.month===e.month}toPlainDate(){return new Ct(this.year,this.month,1)}}function ha(n,e){if(e)try{return n.from(e)}catch{}}function Ni(n){const[e,t]=vu(n);return[pi(()=>ha(Ct,e),[e]),i=>t(i?.toString())]}function Pv(n){const[e="",t]=vu(n);return[pi(()=>{const[i,r]=e.split("/"),s=ha(Ct,i),o=ha(Ct,r);return s&&o?[s,o]:[]},[e]),i=>t(`${i[0]}/${i[1]}`)]}function Rv(n){const[e="",t]=vu(n);return[pi(()=>{const i=[];for(const r of e.trim().split(/\s+/)){const s=ha(Ct,r);s&&i.push(s)}return i},[e]),i=>t(i.join(" "))]}function Ws(n,e){return pi(()=>new Intl.DateTimeFormat(e,{timeZone:"UTC",...n}),[e,n])}function Ud(n,e,t){const i=Ws(n,t);return pi(()=>{const r=[],s=new Date;for(var o=0;o<7;o++){const a=(s.getUTCDay()-e+7)%7;r[a]=i.format(s),s.setUTCDate(s.getUTCDate()+1)}return r},[e,i])}const Od=(n,e,t)=>La(n,e,t)===n,Fd=n=>n.target.matches(":dir(ltr)"),Dv={month:"long",day:"numeric"},Lv={month:"long"},Iv={weekday:"long"},sl={bubbles:!0};function Uv({props:n,context:e}){const{offset:t}=n,{firstDayOfWeek:i,isDateDisallowed:r,min:s,max:o,today:a,page:l,locale:c,focusedDate:u,formatWeekday:d}=e,p=a??xu(),f=Ud(Iv,i,c),_=pi(()=>({weekday:d}),[d]),g=Ud(_,i,c),m=Ws(Dv,c),h=Ws(Lv,c),v=pi(()=>l.start.add({months:t}),[l,t]),x=pi(()=>Av(v,i),[v,i]),w=Fi("focusday",sl),S=Fi("selectday",sl),C=Fi("hoverday",sl);function T(y){w(La(y,s,o))}function A(y){let P;switch(y.key){case"ArrowRight":P=u.add({days:Fd(y)?1:-1});break;case"ArrowLeft":P=u.add({days:Fd(y)?-1:1});break;case"ArrowDown":P=u.add({days:7});break;case"ArrowUp":P=u.add({days:-7});break;case"PageUp":P=u.add(y.shiftKey?{years:-1}:{months:-1});break;case"PageDown":P=u.add(y.shiftKey?{years:1}:{months:1});break;case"Home":P=wu(u,i);break;case"End":P=Gf(u,i);break;default:return}T(P),y.preventDefault()}function b(y){const P=v.equals(y);if(!e.showOutsideDays&&!P)return;const D=y.equals(u),O=y.equals(p),V=Bn(y),k=r?.(V),G=!Od(y,s,o);let $="",U;if(e.type==="range"){const[Z,ee]=e.value,ce=Z?.equals(y),Ae=ee?.equals(y);U=Z&&ee&&Od(y,Z,ee),$=`${ce?"range-start":""} ${Ae?"range-end":""} ${U&&!ce&&!Ae?"range-inner":""}`}else e.type==="multi"?U=e.value.some(Z=>Z.equals(y)):U=e.value?.equals(y);return{part:`${`button day day-${V.getDay()} ${P?U?"selected":"":"outside"} ${k?"disallowed":""} ${O?"today":""} ${e.getDayParts?.(V)??""}`} ${$}`,tabindex:P&&D?0:-1,disabled:G,"aria-disabled":k?"true":void 0,"aria-pressed":P&&U,"aria-current":O?"date":void 0,"aria-label":m.format(V),onkeydown:A,onclick(){k||S(y),T(y)},onmouseover(){!k&&!G&&C(y)}}}return{weeks:x,yearMonth:v,daysLong:f,daysVisible:g,formatter:h,getDayProps:b}}const ol=xu(),yu=Mv({type:"date",firstDayOfWeek:1,focusedDate:ol,page:{start:ol.toPlainYearMonth(),end:ol.toPlainYearMonth()}});customElements.define("calendar-ctx",yu);const Ov=(n,e)=>(e+n)%7,Fv=lo(n=>{const e=Ev(yu),t=Y_(),i=Uv({props:n,context:e});function r(){t.current.querySelector("button[tabindex='0']")?.focus()}return Ns("host",{shadowDom:!0,focus:r,children:[lt("div",{id:"h",part:"heading",children:i.formatter.format(Bn(i.yearMonth))}),Ns("table",{ref:t,"aria-labelledby":"h",part:"table",children:[lt("thead",{children:lt("tr",{part:"tr head",children:i.daysLong.map((s,o)=>Ns("th",{part:`th day day-${Ov(e.firstDayOfWeek,o)}`,scope:"col",children:[lt("span",{class:"vh",children:s}),lt("span",{"aria-hidden":"true",children:i.daysVisible[o]})]}))})}),lt("tbody",{children:i.weeks.map((s,o)=>lt("tr",{part:"tr week",children:s.map((a,l)=>{const c=i.getDayProps(a);return lt("td",{part:"td",children:c&&lt("button",{...c,children:a.day})},l)})},o))})]})]})},{props:{offset:{type:Number,value:0}},styles:[Vf,Hf,Da`:host{--color-accent: black;--color-text-on-accent: white;display:flex;flex-direction:column;gap:.25rem;text-align:center;inline-size:fit-content}table{border-collapse:collapse;font-size:.875rem}th{font-weight:700;block-size:2.25rem}td{padding-inline:0}button{color:inherit;font-size:inherit;background:transparent;border:0;font-variant-numeric:tabular-nums;block-size:2.25rem;inline-size:2.25rem}button:hover:where(:not(:disabled,[aria-disabled])){background:#0000000d}button:is([aria-pressed=true],:focus-visible){background:var(--color-accent);color:var(--color-text-on-accent)}button:focus-visible{outline:1px solid var(--color-text-on-accent);outline-offset:-2px}button:disabled,:host::part(outside),:host::part(disallowed){cursor:default;opacity:.5}`]});customElements.define("calendar-month",Fv);function Nd(n){return lt("button",{part:`button ${n.name} ${n.onclick?"":"disabled"}`,onclick:n.onclick,"aria-disabled":n.onclick?null:"true",children:lt("slot",{name:n.name,children:n.children})})}function bu(n){const e=Bn(n.page.start),t=Bn(n.page.end);return Ns("div",{role:"group","aria-labelledby":"h",part:"container",children:[lt("div",{id:"h",class:"vh","aria-live":"polite","aria-atomic":"true",children:n.formatVerbose.formatRange(e,t)}),Ns("div",{part:"header",children:[lt(Nd,{name:"previous",onclick:n.previous,children:"Previous"}),lt("slot",{part:"heading",name:"heading",children:lt("div",{"aria-hidden":"true",children:n.format.formatRange(e,t)})}),lt(Nd,{name:"next",onclick:n.next,children:"Next"})]}),lt(yu,{value:n,onselectday:n.onSelect,onfocusday:n.onFocus,onhoverday:n.onHover,children:lt("slot",{})})]})}const Su={value:{type:String,value:""},min:{type:String,value:""},max:{type:String,value:""},today:{type:String,value:""},isDateDisallowed:{type:Function,value:n=>!1},formatWeekday:{type:String,value:()=>"narrow"},getDayParts:{type:Function,value:n=>""},firstDayOfWeek:{type:Number,value:()=>1},showOutsideDays:{type:Boolean,value:!1},locale:{type:String,value:()=>{}},months:{type:Number,value:1},focusedDate:{type:String,value:()=>{}},pageBy:{type:String,value:()=>"months"}},Eu=[Vf,Hf,Da`:host{display:block;inline-size:fit-content}[role=group]{display:flex;flex-direction:column;gap:1em}:host::part(header){display:flex;align-items:center;justify-content:space-between}:host::part(heading){font-weight:700;font-size:1.25em}button{display:flex;align-items:center;justify-content:center}button[aria-disabled]{cursor:default;opacity:.5}`],Nv={year:"numeric"},kv={year:"numeric",month:"long"};function al(n,e){return(e.year-n.year)*12+e.month-n.month}const kd=(n,e)=>(n=e===12?new Ia(n.year,1):n,{start:n,end:n.add({months:e-1})});function Bv({pageBy:n,focusedDate:e,months:t,max:i,min:r,goto:s}){const o=n==="single"?1:t,[a,l]=_u(()=>kd(e.toPlainYearMonth(),t)),c=d=>l(kd(a.start.add({months:d}),t)),u=d=>{const p=al(a.start,d.toPlainYearMonth());return p>=0&&p<t};return Gs(()=>{if(u(e))return;const d=al(e.toPlainYearMonth(),a.start);s(e.add({months:d}))},[a.start]),Gs(()=>{if(u(e))return;const d=al(a.start,e.toPlainYearMonth());c(d===-1?-o:d===t?o:Math.floor(d/t)*t)},[e,o,t]),{page:a,previous:!r||!u(r)?()=>c(-o):void 0,next:!i||!u(i)?()=>c(o):void 0}}function Mu({months:n,pageBy:e,locale:t,focusedDate:i,setFocusedDate:r}){const[s]=Ni("min"),[o]=Ni("max"),[a]=Ni("today"),l=Fi("focusday"),c=Fi("change"),u=pi(()=>La(i??a??xu(),s,o),[i,a,s,o]);function d(h){r(h),l(Bn(h))}const{next:p,previous:f,page:_}=Bv({pageBy:e,focusedDate:u,months:n,min:s,max:o,goto:d}),g=ao();function m(h){const v=h?.target??"day";v==="day"?g.current.querySelectorAll("calendar-month").forEach(x=>x.focus(h)):g.current.shadowRoot.querySelector(`[part~='${v}']`).focus(h)}return{format:Ws(Nv,t),formatVerbose:Ws(kv,t),page:_,focusedDate:u,dispatch:c,onFocus(h){h.stopPropagation(),d(h.detail),setTimeout(m)},min:s,max:o,today:a,next:p,previous:f,focus:m}}const zv=lo(n=>{const[e,t]=Ni("value"),[i=e,r]=Ni("focusedDate"),s=Mu({...n,focusedDate:i,setFocusedDate:r});function o(a){t(a.detail),s.dispatch()}return lt("host",{shadowDom:!0,focus:s.focus,children:lt(bu,{...n,...s,type:"date",value:e,onSelect:o})})},{props:Su,styles:Eu});customElements.define("calendar-date",zv);const Bd=(n,e)=>Ct.compare(n,e)<0?[n,e]:[e,n],Vv=lo(n=>{const[e,t]=Pv("value"),[i=e[0],r]=Ni("focusedDate"),s=Mu({...n,focusedDate:i,setFocusedDate:r}),o=Fi("rangestart"),a=Fi("rangeend"),[l,c]=Ni("tentative"),[u,d]=_u();Gs(()=>d(void 0),[l]);function p(m){s.onFocus(m),f(m)}function f(m){m.stopPropagation(),l&&d(m.detail)}function _(m){const h=m.detail;m.stopPropagation(),l?(t(Bd(l,h)),c(void 0),a(Bn(h)),s.dispatch()):(c(h),o(Bn(h)))}const g=l?Bd(l,u??l):e;return lt("host",{shadowDom:!0,focus:s.focus,children:lt(bu,{...n,...s,type:"range",value:g,onFocus:p,onHover:f,onSelect:_})})},{props:{...Su,tentative:{type:String,value:""}},styles:Eu});customElements.define("calendar-range",Vv);const Hv=lo(n=>{const[e,t]=Rv("value"),[i=e[0],r]=Ni("focusedDate"),s=Mu({...n,focusedDate:i,setFocusedDate:r});function o(a){const l=[...e],c=e.findIndex(u=>u.equals(a.detail));c<0?l.push(a.detail):l.splice(c,1),t(l),s.dispatch()}return lt("host",{shadowDom:!0,focus:s.focus,children:lt(bu,{...n,...s,type:"multi",value:e,onSelect:o})})},{props:Su,styles:Eu});customElements.define("calendar-multi",Hv);/*!
* sweetalert2 v11.26.3
* Released under the MIT License.
*/function Xf(n,e,t){if(typeof n=="function"?n===e:n.has(e))return arguments.length<3?e:t;throw new TypeError("Private element is not present on this object")}function Gv(n,e){if(e.has(n))throw new TypeError("Cannot initialize the same private elements twice on an object")}function zd(n,e){return n.get(Xf(n,e))}function Wv(n,e,t){Gv(n,e),e.set(n,t)}function Xv(n,e,t){return n.set(Xf(n,e),t),t}const $v=100,Me={},qv=()=>{Me.previousActiveElement instanceof HTMLElement?(Me.previousActiveElement.focus(),Me.previousActiveElement=null):document.body&&document.body.focus()},Yv=n=>new Promise(e=>{if(!n)return e();const t=window.scrollX,i=window.scrollY;Me.restoreFocusTimeout=setTimeout(()=>{qv(),e()},$v),window.scrollTo(t,i)}),$f="swal2-",jv=["container","shown","height-auto","iosfix","popup","modal","no-backdrop","no-transition","toast","toast-shown","show","hide","close","title","html-container","actions","confirm","deny","cancel","footer","icon","icon-content","image","input","file","range","select","radio","checkbox","label","textarea","inputerror","input-label","validation-message","progress-steps","active-progress-step","progress-step","progress-step-line","loader","loading","styled","top","top-start","top-end","top-left","top-right","center","center-start","center-end","center-left","center-right","bottom","bottom-start","bottom-end","bottom-left","bottom-right","grow-row","grow-column","grow-fullscreen","rtl","timer-progress-bar","timer-progress-bar-container","scrollbar-measure","icon-success","icon-warning","icon-info","icon-question","icon-error","draggable","dragging"],X=jv.reduce((n,e)=>(n[e]=$f+e,n),{}),Kv=["success","warning","info","question","error"],fa=Kv.reduce((n,e)=>(n[e]=$f+e,n),{}),qf="SweetAlert2:",Tu=n=>n.charAt(0).toUpperCase()+n.slice(1),jt=n=>{console.warn(`${qf} ${typeof n=="object"?n.join(" "):n}`)},br=n=>{console.error(`${qf} ${n}`)},Vd=[],Zv=n=>{Vd.includes(n)||(Vd.push(n),jt(n))},Yf=(n,e=null)=>{Zv(`"${n}" is deprecated and will be removed in the next major release.${e?` Use "${e}" instead.`:""}`)},Ua=n=>typeof n=="function"?n():n,Au=n=>n&&typeof n.toPromise=="function",co=n=>Au(n)?n.toPromise():Promise.resolve(n),Cu=n=>n&&Promise.resolve(n)===n,Zt=()=>document.body.querySelector(`.${X.container}`),uo=n=>{const e=Zt();return e?e.querySelector(n):null},wn=n=>uo(`.${n}`),Ye=()=>wn(X.popup),vs=()=>wn(X.icon),Jv=()=>wn(X["icon-content"]),jf=()=>wn(X.title),Pu=()=>wn(X["html-container"]),Kf=()=>wn(X.image),Ru=()=>wn(X["progress-steps"]),Oa=()=>wn(X["validation-message"]),ei=()=>uo(`.${X.actions} .${X.confirm}`),xs=()=>uo(`.${X.actions} .${X.cancel}`),Sr=()=>uo(`.${X.actions} .${X.deny}`),Qv=()=>wn(X["input-label"]),ws=()=>uo(`.${X.loader}`),ho=()=>wn(X.actions),Zf=()=>wn(X.footer),Fa=()=>wn(X["timer-progress-bar"]),Du=()=>wn(X.close),e0=`
  a[href],
  area[href],
  input:not([disabled]),
  select:not([disabled]),
  textarea:not([disabled]),
  button:not([disabled]),
  iframe,
  object,
  embed,
  [tabindex="0"],
  [contenteditable],
  audio[controls],
  video[controls],
  summary
`,Lu=()=>{const n=Ye();if(!n)return[];const e=n.querySelectorAll('[tabindex]:not([tabindex="-1"]):not([tabindex="0"])'),t=Array.from(e).sort((s,o)=>{const a=parseInt(s.getAttribute("tabindex")||"0"),l=parseInt(o.getAttribute("tabindex")||"0");return a>l?1:a<l?-1:0}),i=n.querySelectorAll(e0),r=Array.from(i).filter(s=>s.getAttribute("tabindex")!=="-1");return[...new Set(t.concat(r))].filter(s=>en(s))},Iu=()=>mi(document.body,X.shown)&&!mi(document.body,X["toast-shown"])&&!mi(document.body,X["no-backdrop"]),Na=()=>{const n=Ye();return n?mi(n,X.toast):!1},t0=()=>{const n=Ye();return n?n.hasAttribute("data-loading"):!1},yn=(n,e)=>{if(n.textContent="",e){const i=new DOMParser().parseFromString(e,"text/html"),r=i.querySelector("head");r&&Array.from(r.childNodes).forEach(o=>{n.appendChild(o)});const s=i.querySelector("body");s&&Array.from(s.childNodes).forEach(o=>{o instanceof HTMLVideoElement||o instanceof HTMLAudioElement?n.appendChild(o.cloneNode(!0)):n.appendChild(o)})}},mi=(n,e)=>{if(!e)return!1;const t=e.split(/\s+/);for(let i=0;i<t.length;i++)if(!n.classList.contains(t[i]))return!1;return!0},n0=(n,e)=>{Array.from(n.classList).forEach(t=>{!Object.values(X).includes(t)&&!Object.values(fa).includes(t)&&!Object.values(e.showClass||{}).includes(t)&&n.classList.remove(t)})},_n=(n,e,t)=>{if(n0(n,e),!e.customClass)return;const i=e.customClass[t];if(i){if(typeof i!="string"&&!i.forEach){jt(`Invalid type of customClass.${t}! Expected string or iterable object, got "${typeof i}"`);return}je(n,i)}},ka=(n,e)=>{if(!e)return null;switch(e){case"select":case"textarea":case"file":return n.querySelector(`.${X.popup} > .${X[e]}`);case"checkbox":return n.querySelector(`.${X.popup} > .${X.checkbox} input`);case"radio":return n.querySelector(`.${X.popup} > .${X.radio} input:checked`)||n.querySelector(`.${X.popup} > .${X.radio} input:first-child`);case"range":return n.querySelector(`.${X.popup} > .${X.range} input`);default:return n.querySelector(`.${X.popup} > .${X.input}`)}},Jf=n=>{if(n.focus(),n.type!=="file"){const e=n.value;n.value="",n.value=e}},Qf=(n,e,t)=>{!n||!e||(typeof e=="string"&&(e=e.split(/\s+/).filter(Boolean)),e.forEach(i=>{Array.isArray(n)?n.forEach(r=>{t?r.classList.add(i):r.classList.remove(i)}):t?n.classList.add(i):n.classList.remove(i)}))},je=(n,e)=>{Qf(n,e,!0)},Ln=(n,e)=>{Qf(n,e,!1)},Di=(n,e)=>{const t=Array.from(n.children);for(let i=0;i<t.length;i++){const r=t[i];if(r instanceof HTMLElement&&mi(r,e))return r}},dr=(n,e,t)=>{t===`${parseInt(`${t}`)}`&&(t=parseInt(t)),t||parseInt(`${t}`)===0?n.style.setProperty(e,typeof t=="number"?`${t}px`:t):n.style.removeProperty(e)},Ut=(n,e="flex")=>{n&&(n.style.display=e)},Ht=n=>{n&&(n.style.display="none")},Uu=(n,e="block")=>{n&&new MutationObserver(()=>{fo(n,n.innerHTML,e)}).observe(n,{childList:!0,subtree:!0})},Hd=(n,e,t,i)=>{const r=n.querySelector(e);r&&r.style.setProperty(t,i)},fo=(n,e,t="flex")=>{e?Ut(n,t):Ht(n)},en=n=>!!(n&&(n.offsetWidth||n.offsetHeight||n.getClientRects().length)),i0=()=>!en(ei())&&!en(Sr())&&!en(xs()),sc=n=>n.scrollHeight>n.clientHeight,r0=(n,e)=>{let t=n;for(;t&&t!==e;){if(sc(t))return!0;t=t.parentElement}return!1},ep=n=>{const e=window.getComputedStyle(n),t=parseFloat(e.getPropertyValue("animation-duration")||"0"),i=parseFloat(e.getPropertyValue("transition-duration")||"0");return t>0||i>0},Ou=(n,e=!1)=>{const t=Fa();t&&en(t)&&(e&&(t.style.transition="none",t.style.width="100%"),setTimeout(()=>{t.style.transition=`width ${n/1e3}s linear`,t.style.width="0%"},10))},s0=()=>{const n=Fa();if(!n)return;const e=parseInt(window.getComputedStyle(n).width);n.style.removeProperty("transition"),n.style.width="100%";const t=parseInt(window.getComputedStyle(n).width),i=e/t*100;n.style.width=`${i}%`},o0=()=>typeof window>"u"||typeof document>"u",a0=`
 <div aria-labelledby="${X.title}" aria-describedby="${X["html-container"]}" class="${X.popup}" tabindex="-1">
   <button type="button" class="${X.close}"></button>
   <ul class="${X["progress-steps"]}"></ul>
   <div class="${X.icon}"></div>
   <img class="${X.image}" />
   <h2 class="${X.title}" id="${X.title}"></h2>
   <div class="${X["html-container"]}" id="${X["html-container"]}"></div>
   <input class="${X.input}" id="${X.input}" />
   <input type="file" class="${X.file}" />
   <div class="${X.range}">
     <input type="range" />
     <output></output>
   </div>
   <select class="${X.select}" id="${X.select}"></select>
   <div class="${X.radio}"></div>
   <label class="${X.checkbox}">
     <input type="checkbox" id="${X.checkbox}" />
     <span class="${X.label}"></span>
   </label>
   <textarea class="${X.textarea}" id="${X.textarea}"></textarea>
   <div class="${X["validation-message"]}" id="${X["validation-message"]}"></div>
   <div class="${X.actions}">
     <div class="${X.loader}"></div>
     <button type="button" class="${X.confirm}"></button>
     <button type="button" class="${X.deny}"></button>
     <button type="button" class="${X.cancel}"></button>
   </div>
   <div class="${X.footer}"></div>
   <div class="${X["timer-progress-bar-container"]}">
     <div class="${X["timer-progress-bar"]}"></div>
   </div>
 </div>
`.replace(/(^|\n)\s*/g,""),l0=()=>{const n=Zt();return n?(n.remove(),Ln([document.documentElement,document.body],[X["no-backdrop"],X["toast-shown"],X["has-column"]]),!0):!1},Yi=()=>{Me.currentInstance.resetValidationMessage()},c0=()=>{const n=Ye(),e=Di(n,X.input),t=Di(n,X.file),i=n.querySelector(`.${X.range} input`),r=n.querySelector(`.${X.range} output`),s=Di(n,X.select),o=n.querySelector(`.${X.checkbox} input`),a=Di(n,X.textarea);e.oninput=Yi,t.onchange=Yi,s.onchange=Yi,o.onchange=Yi,a.oninput=Yi,i.oninput=()=>{Yi(),r.value=i.value},i.onchange=()=>{Yi(),r.value=i.value}},u0=n=>typeof n=="string"?document.querySelector(n):n,d0=n=>{const e=Ye();e.setAttribute("role",n.toast?"alert":"dialog"),e.setAttribute("aria-live",n.toast?"polite":"assertive"),n.toast||e.setAttribute("aria-modal","true")},h0=n=>{window.getComputedStyle(n).direction==="rtl"&&je(Zt(),X.rtl)},f0=n=>{const e=l0();if(o0()){br("SweetAlert2 requires document to initialize");return}const t=document.createElement("div");t.className=X.container,e&&je(t,X["no-transition"]),yn(t,a0),t.dataset.swal2Theme=n.theme;const i=u0(n.target);i.appendChild(t),n.topLayer&&(t.setAttribute("popover",""),t.showPopover()),d0(n),h0(i),c0()},Fu=(n,e)=>{n instanceof HTMLElement?e.appendChild(n):typeof n=="object"?p0(n,e):n&&yn(e,n)},p0=(n,e)=>{n.jquery?m0(e,n):yn(e,n.toString())},m0=(n,e)=>{if(n.textContent="",0 in e)for(let t=0;t in e;t++)n.appendChild(e[t].cloneNode(!0));else n.appendChild(e.cloneNode(!0))},g0=(n,e)=>{const t=ho(),i=ws();!t||!i||(!e.showConfirmButton&&!e.showDenyButton&&!e.showCancelButton?Ht(t):Ut(t),_n(t,e,"actions"),_0(t,i,e),yn(i,e.loaderHtml||""),_n(i,e,"loader"))};function _0(n,e,t){const i=ei(),r=Sr(),s=xs();!i||!r||!s||(cl(i,"confirm",t),cl(r,"deny",t),cl(s,"cancel",t),v0(i,r,s,t),t.reverseButtons&&(t.toast?(n.insertBefore(s,i),n.insertBefore(r,i)):(n.insertBefore(s,e),n.insertBefore(r,e),n.insertBefore(i,e))))}function v0(n,e,t,i){if(!i.buttonsStyling){Ln([n,e,t],X.styled);return}je([n,e,t],X.styled),i.confirmButtonColor&&n.style.setProperty("--swal2-confirm-button-background-color",i.confirmButtonColor),i.denyButtonColor&&e.style.setProperty("--swal2-deny-button-background-color",i.denyButtonColor),i.cancelButtonColor&&t.style.setProperty("--swal2-cancel-button-background-color",i.cancelButtonColor),ll(n),ll(e),ll(t)}function ll(n){const e=window.getComputedStyle(n);if(e.getPropertyValue("--swal2-action-button-focus-box-shadow"))return;const t=e.backgroundColor.replace(/rgba?\((\d+), (\d+), (\d+).*/,"rgba($1, $2, $3, 0.5)");n.style.setProperty("--swal2-action-button-focus-box-shadow",e.getPropertyValue("--swal2-outline").replace(/ rgba\(.*/,` ${t}`))}function cl(n,e,t){const i=Tu(e);fo(n,t[`show${i}Button`],"inline-block"),yn(n,t[`${e}ButtonText`]||""),n.setAttribute("aria-label",t[`${e}ButtonAriaLabel`]||""),n.className=X[e],_n(n,t,`${e}Button`)}const x0=(n,e)=>{const t=Du();t&&(yn(t,e.closeButtonHtml||""),_n(t,e,"closeButton"),fo(t,e.showCloseButton),t.setAttribute("aria-label",e.closeButtonAriaLabel||""))},w0=(n,e)=>{const t=Zt();t&&(y0(t,e.backdrop),b0(t,e.position),S0(t,e.grow),_n(t,e,"container"))};function y0(n,e){typeof e=="string"?n.style.background=e:e||je([document.documentElement,document.body],X["no-backdrop"])}function b0(n,e){e&&(e in X?je(n,X[e]):(jt('The "position" parameter is not valid, defaulting to "center"'),je(n,X.center)))}function S0(n,e){e&&je(n,X[`grow-${e}`])}var ot={innerParams:new WeakMap,domCache:new WeakMap};const E0=["input","file","range","select","radio","checkbox","textarea"],M0=(n,e)=>{const t=Ye();if(!t)return;const i=ot.innerParams.get(n),r=!i||e.input!==i.input;E0.forEach(s=>{const o=Di(t,X[s]);o&&(C0(s,e.inputAttributes),o.className=X[s],r&&Ht(o))}),e.input&&(r&&T0(e),P0(e))},T0=n=>{if(!n.input)return;if(!xt[n.input]){br(`Unexpected type of input! Expected ${Object.keys(xt).join(" | ")}, got "${n.input}"`);return}const e=tp(n.input);if(!e)return;const t=xt[n.input](e,n);Ut(e),n.inputAutoFocus&&setTimeout(()=>{Jf(t)})},A0=n=>{for(let e=0;e<n.attributes.length;e++){const t=n.attributes[e].name;["id","type","value","style"].includes(t)||n.removeAttribute(t)}},C0=(n,e)=>{const t=Ye();if(!t)return;const i=ka(t,n);if(i){A0(i);for(const r in e)i.setAttribute(r,e[r])}},P0=n=>{if(!n.input)return;const e=tp(n.input);e&&_n(e,n,"input")},Nu=(n,e)=>{!n.placeholder&&e.inputPlaceholder&&(n.placeholder=e.inputPlaceholder)},po=(n,e,t)=>{if(t.inputLabel){const i=document.createElement("label"),r=X["input-label"];i.setAttribute("for",n.id),i.className=r,typeof t.customClass=="object"&&je(i,t.customClass.inputLabel),i.innerText=t.inputLabel,e.insertAdjacentElement("beforebegin",i)}},tp=n=>{const e=Ye();if(e)return Di(e,X[n]||X.input)},pa=(n,e)=>{["string","number"].includes(typeof e)?n.value=`${e}`:Cu(e)||jt(`Unexpected type of inputValue! Expected "string", "number" or "Promise", got "${typeof e}"`)},xt={};xt.text=xt.email=xt.password=xt.number=xt.tel=xt.url=xt.search=xt.date=xt["datetime-local"]=xt.time=xt.week=xt.month=(n,e)=>(pa(n,e.inputValue),po(n,n,e),Nu(n,e),n.type=e.input,n);xt.file=(n,e)=>(po(n,n,e),Nu(n,e),n);xt.range=(n,e)=>{const t=n.querySelector("input"),i=n.querySelector("output");return pa(t,e.inputValue),t.type=e.input,pa(i,e.inputValue),po(t,n,e),n};xt.select=(n,e)=>{if(n.textContent="",e.inputPlaceholder){const t=document.createElement("option");yn(t,e.inputPlaceholder),t.value="",t.disabled=!0,t.selected=!0,n.appendChild(t)}return po(n,n,e),n};xt.radio=n=>(n.textContent="",n);xt.checkbox=(n,e)=>{const t=ka(Ye(),"checkbox");t.value="1",t.checked=!!e.inputValue;const i=n.querySelector("span");return yn(i,e.inputPlaceholder||e.inputLabel),t};xt.textarea=(n,e)=>{pa(n,e.inputValue),Nu(n,e),po(n,n,e);const t=i=>parseInt(window.getComputedStyle(i).marginLeft)+parseInt(window.getComputedStyle(i).marginRight);return setTimeout(()=>{if("MutationObserver"in window){const i=parseInt(window.getComputedStyle(Ye()).width),r=()=>{if(!document.body.contains(n))return;const s=n.offsetWidth+t(n);s>i?Ye().style.width=`${s}px`:dr(Ye(),"width",e.width)};new MutationObserver(r).observe(n,{attributes:!0,attributeFilter:["style"]})}}),n};const R0=(n,e)=>{const t=Pu();t&&(Uu(t),_n(t,e,"htmlContainer"),e.html?(Fu(e.html,t),Ut(t,"block")):e.text?(t.textContent=e.text,Ut(t,"block")):Ht(t),M0(n,e))},D0=(n,e)=>{const t=Zf();t&&(Uu(t),fo(t,!!e.footer,"block"),e.footer&&Fu(e.footer,t),_n(t,e,"footer"))},L0=(n,e)=>{const t=ot.innerParams.get(n),i=vs();if(!i)return;if(t&&e.icon===t.icon){Wd(i,e),Gd(i,e);return}if(!e.icon&&!e.iconHtml){Ht(i);return}if(e.icon&&Object.keys(fa).indexOf(e.icon)===-1){br(`Unknown icon! Expected "success", "error", "warning", "info" or "question", got "${e.icon}"`),Ht(i);return}Ut(i),Wd(i,e),Gd(i,e),je(i,e.showClass&&e.showClass.icon),window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change",np)},Gd=(n,e)=>{for(const[t,i]of Object.entries(fa))e.icon!==t&&Ln(n,i);je(n,e.icon&&fa[e.icon]),O0(n,e),np(),_n(n,e,"icon")},np=()=>{const n=Ye();if(!n)return;const e=window.getComputedStyle(n).getPropertyValue("background-color"),t=n.querySelectorAll("[class^=swal2-success-circular-line], .swal2-success-fix");for(let i=0;i<t.length;i++)t[i].style.backgroundColor=e},I0=n=>`
  ${n.animation?'<div class="swal2-success-circular-line-left"></div>':""}
  <span class="swal2-success-line-tip"></span> <span class="swal2-success-line-long"></span>
  <div class="swal2-success-ring"></div>
  ${n.animation?'<div class="swal2-success-fix"></div>':""}
  ${n.animation?'<div class="swal2-success-circular-line-right"></div>':""}
`,U0=`
  <span class="swal2-x-mark">
    <span class="swal2-x-mark-line-left"></span>
    <span class="swal2-x-mark-line-right"></span>
  </span>
`,Wd=(n,e)=>{if(!e.icon&&!e.iconHtml)return;let t=n.innerHTML,i="";e.iconHtml?i=Xd(e.iconHtml):e.icon==="success"?(i=I0(e),t=t.replace(/ style=".*?"/g,"")):e.icon==="error"?i=U0:e.icon&&(i=Xd({question:"?",warning:"!",info:"i"}[e.icon])),t.trim()!==i.trim()&&yn(n,i)},O0=(n,e)=>{if(e.iconColor){n.style.color=e.iconColor,n.style.borderColor=e.iconColor;for(const t of[".swal2-success-line-tip",".swal2-success-line-long",".swal2-x-mark-line-left",".swal2-x-mark-line-right"])Hd(n,t,"background-color",e.iconColor);Hd(n,".swal2-success-ring","border-color",e.iconColor)}},Xd=n=>`<div class="${X["icon-content"]}">${n}</div>`,F0=(n,e)=>{const t=Kf();if(t){if(!e.imageUrl){Ht(t);return}Ut(t,""),t.setAttribute("src",e.imageUrl),t.setAttribute("alt",e.imageAlt||""),dr(t,"width",e.imageWidth),dr(t,"height",e.imageHeight),t.className=X.image,_n(t,e,"image")}};let ku=!1,ip=0,rp=0,sp=0,op=0;const N0=n=>{n.addEventListener("mousedown",ma),document.body.addEventListener("mousemove",ga),n.addEventListener("mouseup",_a),n.addEventListener("touchstart",ma),document.body.addEventListener("touchmove",ga),n.addEventListener("touchend",_a)},k0=n=>{n.removeEventListener("mousedown",ma),document.body.removeEventListener("mousemove",ga),n.removeEventListener("mouseup",_a),n.removeEventListener("touchstart",ma),document.body.removeEventListener("touchmove",ga),n.removeEventListener("touchend",_a)},ma=n=>{const e=Ye();if(n.target===e||vs().contains(n.target)){ku=!0;const t=ap(n);ip=t.clientX,rp=t.clientY,sp=parseInt(e.style.insetInlineStart)||0,op=parseInt(e.style.insetBlockStart)||0,je(e,"swal2-dragging")}},ga=n=>{const e=Ye();if(ku){let{clientX:t,clientY:i}=ap(n);e.style.insetInlineStart=`${sp+(t-ip)}px`,e.style.insetBlockStart=`${op+(i-rp)}px`}},_a=()=>{const n=Ye();ku=!1,Ln(n,"swal2-dragging")},ap=n=>{let e=0,t=0;return n.type.startsWith("mouse")?(e=n.clientX,t=n.clientY):n.type.startsWith("touch")&&(e=n.touches[0].clientX,t=n.touches[0].clientY),{clientX:e,clientY:t}},B0=(n,e)=>{const t=Zt(),i=Ye();if(!(!t||!i)){if(e.toast){dr(t,"width",e.width),i.style.width="100%";const r=ws();r&&i.insertBefore(r,vs())}else dr(i,"width",e.width);dr(i,"padding",e.padding),e.color&&(i.style.color=e.color),e.background&&(i.style.background=e.background),Ht(Oa()),z0(i,e),e.draggable&&!e.toast?(je(i,X.draggable),N0(i)):(Ln(i,X.draggable),k0(i))}},z0=(n,e)=>{const t=e.showClass||{};n.className=`${X.popup} ${en(n)?t.popup:""}`,e.toast?(je([document.documentElement,document.body],X["toast-shown"]),je(n,X.toast)):je(n,X.modal),_n(n,e,"popup"),typeof e.customClass=="string"&&je(n,e.customClass),e.icon&&je(n,X[`icon-${e.icon}`])},V0=(n,e)=>{const t=Ru();if(!t)return;const{progressSteps:i,currentProgressStep:r}=e;if(!i||i.length===0||r===void 0){Ht(t);return}Ut(t),t.textContent="",r>=i.length&&jt("Invalid currentProgressStep parameter, it should be less than progressSteps.length (currentProgressStep like JS arrays starts from 0)"),i.forEach((s,o)=>{const a=H0(s);if(t.appendChild(a),o===r&&je(a,X["active-progress-step"]),o!==i.length-1){const l=G0(e);t.appendChild(l)}})},H0=n=>{const e=document.createElement("li");return je(e,X["progress-step"]),yn(e,n),e},G0=n=>{const e=document.createElement("li");return je(e,X["progress-step-line"]),n.progressStepsDistance&&dr(e,"width",n.progressStepsDistance),e},W0=(n,e)=>{const t=jf();t&&(Uu(t),fo(t,!!(e.title||e.titleText),"block"),e.title&&Fu(e.title,t),e.titleText&&(t.innerText=e.titleText),_n(t,e,"title"))},lp=(n,e)=>{B0(n,e),w0(n,e),V0(n,e),L0(n,e),F0(n,e),W0(n,e),x0(n,e),R0(n,e),g0(n,e),D0(n,e);const t=Ye();typeof e.didRender=="function"&&t&&e.didRender(t),Me.eventEmitter.emit("didRender",t)},X0=()=>en(Ye()),cp=()=>{var n;return(n=ei())===null||n===void 0?void 0:n.click()},$0=()=>{var n;return(n=Sr())===null||n===void 0?void 0:n.click()},q0=()=>{var n;return(n=xs())===null||n===void 0?void 0:n.click()},ys=Object.freeze({cancel:"cancel",backdrop:"backdrop",close:"close",esc:"esc",timer:"timer"}),up=n=>{n.keydownTarget&&n.keydownHandlerAdded&&(n.keydownTarget.removeEventListener("keydown",n.keydownHandler,{capture:n.keydownListenerCapture}),n.keydownHandlerAdded=!1)},Y0=(n,e,t)=>{up(n),e.toast||(n.keydownHandler=i=>K0(e,i,t),n.keydownTarget=e.keydownListenerCapture?window:Ye(),n.keydownListenerCapture=e.keydownListenerCapture,n.keydownTarget.addEventListener("keydown",n.keydownHandler,{capture:n.keydownListenerCapture}),n.keydownHandlerAdded=!0)},oc=(n,e)=>{var t;const i=Lu();if(i.length){n=n+e,n===-2&&(n=i.length-1),n===i.length?n=0:n===-1&&(n=i.length-1),i[n].focus();return}(t=Ye())===null||t===void 0||t.focus()},dp=["ArrowRight","ArrowDown"],j0=["ArrowLeft","ArrowUp"],K0=(n,e,t)=>{n&&(e.isComposing||e.keyCode===229||(n.stopKeydownPropagation&&e.stopPropagation(),e.key==="Enter"?Z0(e,n):e.key==="Tab"?J0(e):[...dp,...j0].includes(e.key)?Q0(e.key):e.key==="Escape"&&ex(e,n,t)))},Z0=(n,e)=>{if(!Ua(e.allowEnterKey))return;const t=ka(Ye(),e.input);if(n.target&&t&&n.target instanceof HTMLElement&&n.target.outerHTML===t.outerHTML){if(["textarea","file"].includes(e.input))return;cp(),n.preventDefault()}},J0=n=>{const e=n.target,t=Lu();let i=-1;for(let r=0;r<t.length;r++)if(e===t[r]){i=r;break}n.shiftKey?oc(i,-1):oc(i,1),n.stopPropagation(),n.preventDefault()},Q0=n=>{const e=ho(),t=ei(),i=Sr(),r=xs();if(!e||!t||!i||!r)return;const s=[t,i,r];if(document.activeElement instanceof HTMLElement&&!s.includes(document.activeElement))return;const o=dp.includes(n)?"nextElementSibling":"previousElementSibling";let a=document.activeElement;if(a){for(let l=0;l<e.children.length;l++){if(a=a[o],!a)return;if(a instanceof HTMLButtonElement&&en(a))break}a instanceof HTMLButtonElement&&a.focus()}},ex=(n,e,t)=>{n.preventDefault(),Ua(e.allowEscapeKey)&&t(ys.esc)};var is={swalPromiseResolve:new WeakMap,swalPromiseReject:new WeakMap};const tx=()=>{const n=Zt();Array.from(document.body.children).forEach(t=>{t.contains(n)||(t.hasAttribute("aria-hidden")&&t.setAttribute("data-previous-aria-hidden",t.getAttribute("aria-hidden")||""),t.setAttribute("aria-hidden","true"))})},hp=()=>{Array.from(document.body.children).forEach(e=>{e.hasAttribute("data-previous-aria-hidden")?(e.setAttribute("aria-hidden",e.getAttribute("data-previous-aria-hidden")||""),e.removeAttribute("data-previous-aria-hidden")):e.removeAttribute("aria-hidden")})},fp=typeof window<"u"&&!!window.GestureEvent,nx=()=>{if(fp&&!mi(document.body,X.iosfix)){const n=document.body.scrollTop;document.body.style.top=`${n*-1}px`,je(document.body,X.iosfix),ix()}},ix=()=>{const n=Zt();if(!n)return;let e;n.ontouchstart=t=>{e=rx(t)},n.ontouchmove=t=>{e&&(t.preventDefault(),t.stopPropagation())}},rx=n=>{const e=n.target,t=Zt(),i=Pu();return!t||!i||sx(n)||ox(n)?!1:e===t||!sc(t)&&e instanceof HTMLElement&&!r0(e,i)&&e.tagName!=="INPUT"&&e.tagName!=="TEXTAREA"&&!(sc(i)&&i.contains(e))},sx=n=>n.touches&&n.touches.length&&n.touches[0].touchType==="stylus",ox=n=>n.touches&&n.touches.length>1,ax=()=>{if(mi(document.body,X.iosfix)){const n=parseInt(document.body.style.top,10);Ln(document.body,X.iosfix),document.body.style.top="",document.body.scrollTop=n*-1}},lx=()=>{const n=document.createElement("div");n.className=X["scrollbar-measure"],document.body.appendChild(n);const e=n.getBoundingClientRect().width-n.clientWidth;return document.body.removeChild(n),e};let Yr=null;const cx=n=>{Yr===null&&(document.body.scrollHeight>window.innerHeight||n==="scroll")&&(Yr=parseInt(window.getComputedStyle(document.body).getPropertyValue("padding-right")),document.body.style.paddingRight=`${Yr+lx()}px`)},ux=()=>{Yr!==null&&(document.body.style.paddingRight=`${Yr}px`,Yr=null)};function pp(n,e,t,i){Na()?$d(n,i):(Yv(t).then(()=>$d(n,i)),up(Me)),fp?(e.setAttribute("style","display:none !important"),e.removeAttribute("class"),e.innerHTML=""):e.remove(),Iu()&&(ux(),ax(),hp()),dx()}function dx(){Ln([document.documentElement,document.body],[X.shown,X["height-auto"],X["no-backdrop"],X["toast-shown"]])}function Li(n){n=fx(n);const e=is.swalPromiseResolve.get(this),t=hx(this);this.isAwaitingPromise?n.isDismissed||(mo(this),e(n)):t&&e(n)}const hx=n=>{const e=Ye();if(!e)return!1;const t=ot.innerParams.get(n);if(!t||mi(e,t.hideClass.popup))return!1;Ln(e,t.showClass.popup),je(e,t.hideClass.popup);const i=Zt();return Ln(i,t.showClass.backdrop),je(i,t.hideClass.backdrop),px(n,e,t),!0};function mp(n){const e=is.swalPromiseReject.get(this);mo(this),e&&e(n)}const mo=n=>{n.isAwaitingPromise&&(delete n.isAwaitingPromise,ot.innerParams.get(n)||n._destroy())},fx=n=>typeof n>"u"?{isConfirmed:!1,isDenied:!1,isDismissed:!0}:Object.assign({isConfirmed:!1,isDenied:!1,isDismissed:!1},n),px=(n,e,t)=>{var i;const r=Zt(),s=ep(e);typeof t.willClose=="function"&&t.willClose(e),(i=Me.eventEmitter)===null||i===void 0||i.emit("willClose",e),s?mx(n,e,r,t.returnFocus,t.didClose):pp(n,r,t.returnFocus,t.didClose)},mx=(n,e,t,i,r)=>{Me.swalCloseEventFinishedCallback=pp.bind(null,n,t,i,r);const s=function(o){if(o.target===e){var a;(a=Me.swalCloseEventFinishedCallback)===null||a===void 0||a.call(Me),delete Me.swalCloseEventFinishedCallback,e.removeEventListener("animationend",s),e.removeEventListener("transitionend",s)}};e.addEventListener("animationend",s),e.addEventListener("transitionend",s)},$d=(n,e)=>{setTimeout(()=>{var t;typeof e=="function"&&e.bind(n.params)(),(t=Me.eventEmitter)===null||t===void 0||t.emit("didClose"),n._destroy&&n._destroy()})},rs=n=>{let e=Ye();if(e||new Xs,e=Ye(),!e)return;const t=ws();Na()?Ht(vs()):gx(e,n),Ut(t),e.setAttribute("data-loading","true"),e.setAttribute("aria-busy","true"),e.focus()},gx=(n,e)=>{const t=ho(),i=ws();!t||!i||(!e&&en(ei())&&(e=ei()),Ut(t),e&&(Ht(e),i.setAttribute("data-button-to-replace",e.className),t.insertBefore(i,e)),je([n,t],X.loading))},_x=(n,e)=>{e.input==="select"||e.input==="radio"?bx(n,e):["text","email","number","tel","textarea"].some(t=>t===e.input)&&(Au(e.inputValue)||Cu(e.inputValue))&&(rs(ei()),Sx(n,e))},vx=(n,e)=>{const t=n.getInput();if(!t)return null;switch(e.input){case"checkbox":return xx(t);case"radio":return wx(t);case"file":return yx(t);default:return e.inputAutoTrim?t.value.trim():t.value}},xx=n=>n.checked?1:0,wx=n=>n.checked?n.value:null,yx=n=>n.files&&n.files.length?n.getAttribute("multiple")!==null?n.files:n.files[0]:null,bx=(n,e)=>{const t=Ye();if(!t)return;const i=r=>{e.input==="select"?Ex(t,va(r),e):e.input==="radio"&&Mx(t,va(r),e)};Au(e.inputOptions)||Cu(e.inputOptions)?(rs(ei()),co(e.inputOptions).then(r=>{n.hideLoading(),i(r)})):typeof e.inputOptions=="object"?i(e.inputOptions):br(`Unexpected type of inputOptions! Expected object, Map or Promise, got ${typeof e.inputOptions}`)},Sx=(n,e)=>{const t=n.getInput();t&&(Ht(t),co(e.inputValue).then(i=>{t.value=e.input==="number"?`${parseFloat(i)||0}`:`${i}`,Ut(t),t.focus(),n.hideLoading()}).catch(i=>{br(`Error in inputValue promise: ${i}`),t.value="",Ut(t),t.focus(),n.hideLoading()}))};function Ex(n,e,t){const i=Di(n,X.select);if(!i)return;const r=(s,o,a)=>{const l=document.createElement("option");l.value=a,yn(l,o),l.selected=gp(a,t.inputValue),s.appendChild(l)};e.forEach(s=>{const o=s[0],a=s[1];if(Array.isArray(a)){const l=document.createElement("optgroup");l.label=o,l.disabled=!1,i.appendChild(l),a.forEach(c=>r(l,c[1],c[0]))}else r(i,a,o)}),i.focus()}function Mx(n,e,t){const i=Di(n,X.radio);if(!i)return;e.forEach(s=>{const o=s[0],a=s[1],l=document.createElement("input"),c=document.createElement("label");l.type="radio",l.name=X.radio,l.value=o,gp(o,t.inputValue)&&(l.checked=!0);const u=document.createElement("span");yn(u,a),u.className=X.label,c.appendChild(l),c.appendChild(u),i.appendChild(c)});const r=i.querySelectorAll("input");r.length&&r[0].focus()}const va=n=>{const e=[];return n instanceof Map?n.forEach((t,i)=>{let r=t;typeof r=="object"&&(r=va(r)),e.push([i,r])}):Object.keys(n).forEach(t=>{let i=n[t];typeof i=="object"&&(i=va(i)),e.push([t,i])}),e},gp=(n,e)=>!!e&&e.toString()===n.toString(),Tx=n=>{const e=ot.innerParams.get(n);n.disableButtons(),e.input?_p(n,"confirm"):zu(n,!0)},Ax=n=>{const e=ot.innerParams.get(n);n.disableButtons(),e.returnInputValueOnDeny?_p(n,"deny"):Bu(n,!1)},Cx=(n,e)=>{n.disableButtons(),e(ys.cancel)},_p=(n,e)=>{const t=ot.innerParams.get(n);if(!t.input){br(`The "input" parameter is needed to be set when using returnInputValueOn${Tu(e)}`);return}const i=n.getInput(),r=vx(n,t);t.inputValidator?Px(n,r,e):i&&!i.checkValidity()?(n.enableButtons(),n.showValidationMessage(t.validationMessage||i.validationMessage)):e==="deny"?Bu(n,r):zu(n,r)},Px=(n,e,t)=>{const i=ot.innerParams.get(n);n.disableInput(),Promise.resolve().then(()=>co(i.inputValidator(e,i.validationMessage))).then(s=>{n.enableButtons(),n.enableInput(),s?n.showValidationMessage(s):t==="deny"?Bu(n,e):zu(n,e)})},Bu=(n,e)=>{const t=ot.innerParams.get(n||void 0);t.showLoaderOnDeny&&rs(Sr()),t.preDeny?(n.isAwaitingPromise=!0,Promise.resolve().then(()=>co(t.preDeny(e,t.validationMessage))).then(r=>{r===!1?(n.hideLoading(),mo(n)):n.close({isDenied:!0,value:typeof r>"u"?e:r})}).catch(r=>vp(n||void 0,r))):n.close({isDenied:!0,value:e})},qd=(n,e)=>{n.close({isConfirmed:!0,value:e})},vp=(n,e)=>{n.rejectPromise(e)},zu=(n,e)=>{const t=ot.innerParams.get(n||void 0);t.showLoaderOnConfirm&&rs(),t.preConfirm?(n.resetValidationMessage(),n.isAwaitingPromise=!0,Promise.resolve().then(()=>co(t.preConfirm(e,t.validationMessage))).then(r=>{en(Oa())||r===!1?(n.hideLoading(),mo(n)):qd(n,typeof r>"u"?e:r)}).catch(r=>vp(n||void 0,r))):qd(n,e)};function xa(){const n=ot.innerParams.get(this);if(!n)return;const e=ot.domCache.get(this);Ht(e.loader),Na()?n.icon&&Ut(vs()):Rx(e),Ln([e.popup,e.actions],X.loading),e.popup.removeAttribute("aria-busy"),e.popup.removeAttribute("data-loading"),e.confirmButton.disabled=!1,e.denyButton.disabled=!1,e.cancelButton.disabled=!1}const Rx=n=>{const e=n.popup.getElementsByClassName(n.loader.getAttribute("data-button-to-replace"));e.length?Ut(e[0],"inline-block"):i0()&&Ht(n.actions)};function xp(){const n=ot.innerParams.get(this),e=ot.domCache.get(this);return e?ka(e.popup,n.input):null}function wp(n,e,t){const i=ot.domCache.get(n);e.forEach(r=>{i[r].disabled=t})}function yp(n,e){const t=Ye();if(!(!t||!n))if(n.type==="radio"){const i=t.querySelectorAll(`[name="${X.radio}"]`);for(let r=0;r<i.length;r++)i[r].disabled=e}else n.disabled=e}function bp(){wp(this,["confirmButton","denyButton","cancelButton"],!1)}function Sp(){wp(this,["confirmButton","denyButton","cancelButton"],!0)}function Ep(){yp(this.getInput(),!1)}function Mp(){yp(this.getInput(),!0)}function Tp(n){const e=ot.domCache.get(this),t=ot.innerParams.get(this);yn(e.validationMessage,n),e.validationMessage.className=X["validation-message"],t.customClass&&t.customClass.validationMessage&&je(e.validationMessage,t.customClass.validationMessage),Ut(e.validationMessage);const i=this.getInput();i&&(i.setAttribute("aria-invalid","true"),i.setAttribute("aria-describedby",X["validation-message"]),Jf(i),je(i,X.inputerror))}function Ap(){const n=ot.domCache.get(this);n.validationMessage&&Ht(n.validationMessage);const e=this.getInput();e&&(e.removeAttribute("aria-invalid"),e.removeAttribute("aria-describedby"),Ln(e,X.inputerror))}const jr={title:"",titleText:"",text:"",html:"",footer:"",icon:void 0,iconColor:void 0,iconHtml:void 0,template:void 0,toast:!1,draggable:!1,animation:!0,theme:"light",showClass:{popup:"swal2-show",backdrop:"swal2-backdrop-show",icon:"swal2-icon-show"},hideClass:{popup:"swal2-hide",backdrop:"swal2-backdrop-hide",icon:"swal2-icon-hide"},customClass:{},target:"body",color:void 0,backdrop:!0,heightAuto:!0,allowOutsideClick:!0,allowEscapeKey:!0,allowEnterKey:!0,stopKeydownPropagation:!0,keydownListenerCapture:!1,showConfirmButton:!0,showDenyButton:!1,showCancelButton:!1,preConfirm:void 0,preDeny:void 0,confirmButtonText:"OK",confirmButtonAriaLabel:"",confirmButtonColor:void 0,denyButtonText:"No",denyButtonAriaLabel:"",denyButtonColor:void 0,cancelButtonText:"Cancel",cancelButtonAriaLabel:"",cancelButtonColor:void 0,buttonsStyling:!0,reverseButtons:!1,focusConfirm:!0,focusDeny:!1,focusCancel:!1,returnFocus:!0,showCloseButton:!1,closeButtonHtml:"&times;",closeButtonAriaLabel:"Close this dialog",loaderHtml:"",showLoaderOnConfirm:!1,showLoaderOnDeny:!1,imageUrl:void 0,imageWidth:void 0,imageHeight:void 0,imageAlt:"",timer:void 0,timerProgressBar:!1,width:void 0,padding:void 0,background:void 0,input:void 0,inputPlaceholder:"",inputLabel:"",inputValue:"",inputOptions:{},inputAutoFocus:!0,inputAutoTrim:!0,inputAttributes:{},inputValidator:void 0,returnInputValueOnDeny:!1,validationMessage:void 0,grow:!1,position:"center",progressSteps:[],currentProgressStep:void 0,progressStepsDistance:void 0,willOpen:void 0,didOpen:void 0,didRender:void 0,willClose:void 0,didClose:void 0,didDestroy:void 0,scrollbarPadding:!0,topLayer:!1},Dx=["allowEscapeKey","allowOutsideClick","background","buttonsStyling","cancelButtonAriaLabel","cancelButtonColor","cancelButtonText","closeButtonAriaLabel","closeButtonHtml","color","confirmButtonAriaLabel","confirmButtonColor","confirmButtonText","currentProgressStep","customClass","denyButtonAriaLabel","denyButtonColor","denyButtonText","didClose","didDestroy","draggable","footer","hideClass","html","icon","iconColor","iconHtml","imageAlt","imageHeight","imageUrl","imageWidth","preConfirm","preDeny","progressSteps","returnFocus","reverseButtons","showCancelButton","showCloseButton","showConfirmButton","showDenyButton","text","title","titleText","theme","willClose"],Lx={allowEnterKey:void 0},Ix=["allowOutsideClick","allowEnterKey","backdrop","draggable","focusConfirm","focusDeny","focusCancel","returnFocus","heightAuto","keydownListenerCapture"],Cp=n=>Object.prototype.hasOwnProperty.call(jr,n),Pp=n=>Dx.indexOf(n)!==-1,Rp=n=>Lx[n],Ux=n=>{Cp(n)||jt(`Unknown parameter "${n}"`)},Ox=n=>{Ix.includes(n)&&jt(`The parameter "${n}" is incompatible with toasts`)},Fx=n=>{const e=Rp(n);e&&Yf(n,e)},Dp=n=>{n.backdrop===!1&&n.allowOutsideClick&&jt('"allowOutsideClick" parameter requires `backdrop` parameter to be set to `true`'),n.theme&&!["light","dark","auto","minimal","borderless","bootstrap-4","bootstrap-4-light","bootstrap-4-dark","bootstrap-5","bootstrap-5-light","bootstrap-5-dark","material-ui","material-ui-light","material-ui-dark","embed-iframe","bulma","bulma-light","bulma-dark"].includes(n.theme)&&jt(`Invalid theme "${n.theme}"`);for(const e in n)Ux(e),n.toast&&Ox(e),Fx(e)};function Lp(n){const e=Zt(),t=Ye(),i=ot.innerParams.get(this);if(!t||mi(t,i.hideClass.popup)){jt("You're trying to update the closed or closing popup, that won't work. Use the update() method in preConfirm parameter or show a new popup.");return}const r=Nx(n),s=Object.assign({},i,r);Dp(s),e.dataset.swal2Theme=s.theme,lp(this,s),ot.innerParams.set(this,s),Object.defineProperties(this,{params:{value:Object.assign({},this.params,n),writable:!1,enumerable:!0}})}const Nx=n=>{const e={};return Object.keys(n).forEach(t=>{Pp(t)?e[t]=n[t]:jt(`Invalid parameter to update: ${t}`)}),e};function Ip(){const n=ot.domCache.get(this),e=ot.innerParams.get(this);if(!e){Up(this);return}n.popup&&Me.swalCloseEventFinishedCallback&&(Me.swalCloseEventFinishedCallback(),delete Me.swalCloseEventFinishedCallback),typeof e.didDestroy=="function"&&e.didDestroy(),Me.eventEmitter.emit("didDestroy"),kx(this)}const kx=n=>{Up(n),delete n.params,delete Me.keydownHandler,delete Me.keydownTarget,delete Me.currentInstance},Up=n=>{n.isAwaitingPromise?(ul(ot,n),n.isAwaitingPromise=!0):(ul(is,n),ul(ot,n),delete n.isAwaitingPromise,delete n.disableButtons,delete n.enableButtons,delete n.getInput,delete n.disableInput,delete n.enableInput,delete n.hideLoading,delete n.disableLoading,delete n.showValidationMessage,delete n.resetValidationMessage,delete n.close,delete n.closePopup,delete n.closeModal,delete n.closeToast,delete n.rejectPromise,delete n.update,delete n._destroy)},ul=(n,e)=>{for(const t in n)n[t].delete(e)};var Bx=Object.freeze({__proto__:null,_destroy:Ip,close:Li,closeModal:Li,closePopup:Li,closeToast:Li,disableButtons:Sp,disableInput:Mp,disableLoading:xa,enableButtons:bp,enableInput:Ep,getInput:xp,handleAwaitingPromise:mo,hideLoading:xa,rejectPromise:mp,resetValidationMessage:Ap,showValidationMessage:Tp,update:Lp});const zx=(n,e,t)=>{n.toast?Vx(n,e,t):(Gx(e),Wx(e),Xx(n,e,t))},Vx=(n,e,t)=>{e.popup.onclick=()=>{n&&(Hx(n)||n.timer||n.input)||t(ys.close)}},Hx=n=>!!(n.showConfirmButton||n.showDenyButton||n.showCancelButton||n.showCloseButton);let wa=!1;const Gx=n=>{n.popup.onmousedown=()=>{n.container.onmouseup=function(e){n.container.onmouseup=()=>{},e.target===n.container&&(wa=!0)}}},Wx=n=>{n.container.onmousedown=e=>{e.target===n.container&&e.preventDefault(),n.popup.onmouseup=function(t){n.popup.onmouseup=()=>{},(t.target===n.popup||t.target instanceof HTMLElement&&n.popup.contains(t.target))&&(wa=!0)}}},Xx=(n,e,t)=>{e.container.onclick=i=>{if(wa){wa=!1;return}i.target===e.container&&Ua(n.allowOutsideClick)&&t(ys.backdrop)}},$x=n=>typeof n=="object"&&n.jquery,Yd=n=>n instanceof Element||$x(n),qx=n=>{const e={};return typeof n[0]=="object"&&!Yd(n[0])?Object.assign(e,n[0]):["title","html","icon"].forEach((t,i)=>{const r=n[i];typeof r=="string"||Yd(r)?e[t]=r:r!==void 0&&br(`Unexpected type of ${t}! Expected "string" or "Element", got ${typeof r}`)}),e};function Yx(...n){return new this(...n)}function jx(n){class e extends this{_main(i,r){return super._main(i,Object.assign({},n,r))}}return e}const Kx=()=>Me.timeout&&Me.timeout.getTimerLeft(),Op=()=>{if(Me.timeout)return s0(),Me.timeout.stop()},Fp=()=>{if(Me.timeout){const n=Me.timeout.start();return Ou(n),n}},Zx=()=>{const n=Me.timeout;return n&&(n.running?Op():Fp())},Jx=n=>{if(Me.timeout){const e=Me.timeout.increase(n);return Ou(e,!0),e}},Qx=()=>!!(Me.timeout&&Me.timeout.isRunning());let jd=!1;const ac={};function ew(n="data-swal-template"){ac[n]=this,jd||(document.body.addEventListener("click",tw),jd=!0)}const tw=n=>{for(let e=n.target;e&&e!==document;e=e.parentNode)for(const t in ac){const i=e.getAttribute(t);if(i){ac[t].fire({template:i});return}}};class nw{constructor(){this.events={}}_getHandlersByEventName(e){return typeof this.events[e]>"u"&&(this.events[e]=[]),this.events[e]}on(e,t){const i=this._getHandlersByEventName(e);i.includes(t)||i.push(t)}once(e,t){const i=(...r)=>{this.removeListener(e,i),t.apply(this,r)};this.on(e,i)}emit(e,...t){this._getHandlersByEventName(e).forEach(i=>{try{i.apply(this,t)}catch(r){console.error(r)}})}removeListener(e,t){const i=this._getHandlersByEventName(e),r=i.indexOf(t);r>-1&&i.splice(r,1)}removeAllListeners(e){this.events[e]!==void 0&&(this.events[e].length=0)}reset(){this.events={}}}Me.eventEmitter=new nw;const iw=(n,e)=>{Me.eventEmitter.on(n,e)},rw=(n,e)=>{Me.eventEmitter.once(n,e)},sw=(n,e)=>{if(!n){Me.eventEmitter.reset();return}e?Me.eventEmitter.removeListener(n,e):Me.eventEmitter.removeAllListeners(n)};var ow=Object.freeze({__proto__:null,argsToParams:qx,bindClickHandler:ew,clickCancel:q0,clickConfirm:cp,clickDeny:$0,enableLoading:rs,fire:Yx,getActions:ho,getCancelButton:xs,getCloseButton:Du,getConfirmButton:ei,getContainer:Zt,getDenyButton:Sr,getFocusableElements:Lu,getFooter:Zf,getHtmlContainer:Pu,getIcon:vs,getIconContent:Jv,getImage:Kf,getInputLabel:Qv,getLoader:ws,getPopup:Ye,getProgressSteps:Ru,getTimerLeft:Kx,getTimerProgressBar:Fa,getTitle:jf,getValidationMessage:Oa,increaseTimer:Jx,isDeprecatedParameter:Rp,isLoading:t0,isTimerRunning:Qx,isUpdatableParameter:Pp,isValidParameter:Cp,isVisible:X0,mixin:jx,off:sw,on:iw,once:rw,resumeTimer:Fp,showLoading:rs,stopTimer:Op,toggleTimer:Zx});class aw{constructor(e,t){this.callback=e,this.remaining=t,this.running=!1,this.start()}start(){return this.running||(this.running=!0,this.started=new Date,this.id=setTimeout(this.callback,this.remaining)),this.remaining}stop(){return this.started&&this.running&&(this.running=!1,clearTimeout(this.id),this.remaining-=new Date().getTime()-this.started.getTime()),this.remaining}increase(e){const t=this.running;return t&&this.stop(),this.remaining+=e,t&&this.start(),this.remaining}getTimerLeft(){return this.running&&(this.stop(),this.start()),this.remaining}isRunning(){return this.running}}const Np=["swal-title","swal-html","swal-footer"],lw=n=>{const e=typeof n.template=="string"?document.querySelector(n.template):n.template;if(!e)return{};const t=e.content;return gw(t),Object.assign(cw(t),uw(t),dw(t),hw(t),fw(t),pw(t),mw(t,Np))},cw=n=>{const e={};return Array.from(n.querySelectorAll("swal-param")).forEach(i=>{gr(i,["name","value"]);const r=i.getAttribute("name"),s=i.getAttribute("value");!r||!s||(typeof jr[r]=="boolean"?e[r]=s!=="false":typeof jr[r]=="object"?e[r]=JSON.parse(s):e[r]=s)}),e},uw=n=>{const e={};return Array.from(n.querySelectorAll("swal-function-param")).forEach(i=>{const r=i.getAttribute("name"),s=i.getAttribute("value");!r||!s||(e[r]=new Function(`return ${s}`)())}),e},dw=n=>{const e={};return Array.from(n.querySelectorAll("swal-button")).forEach(i=>{gr(i,["type","color","aria-label"]);const r=i.getAttribute("type");!r||!["confirm","cancel","deny"].includes(r)||(e[`${r}ButtonText`]=i.innerHTML,e[`show${Tu(r)}Button`]=!0,i.hasAttribute("color")&&(e[`${r}ButtonColor`]=i.getAttribute("color")),i.hasAttribute("aria-label")&&(e[`${r}ButtonAriaLabel`]=i.getAttribute("aria-label")))}),e},hw=n=>{const e={},t=n.querySelector("swal-image");return t&&(gr(t,["src","width","height","alt"]),t.hasAttribute("src")&&(e.imageUrl=t.getAttribute("src")||void 0),t.hasAttribute("width")&&(e.imageWidth=t.getAttribute("width")||void 0),t.hasAttribute("height")&&(e.imageHeight=t.getAttribute("height")||void 0),t.hasAttribute("alt")&&(e.imageAlt=t.getAttribute("alt")||void 0)),e},fw=n=>{const e={},t=n.querySelector("swal-icon");return t&&(gr(t,["type","color"]),t.hasAttribute("type")&&(e.icon=t.getAttribute("type")),t.hasAttribute("color")&&(e.iconColor=t.getAttribute("color")),e.iconHtml=t.innerHTML),e},pw=n=>{const e={},t=n.querySelector("swal-input");t&&(gr(t,["type","label","placeholder","value"]),e.input=t.getAttribute("type")||"text",t.hasAttribute("label")&&(e.inputLabel=t.getAttribute("label")),t.hasAttribute("placeholder")&&(e.inputPlaceholder=t.getAttribute("placeholder")),t.hasAttribute("value")&&(e.inputValue=t.getAttribute("value")));const i=Array.from(n.querySelectorAll("swal-input-option"));return i.length&&(e.inputOptions={},i.forEach(r=>{gr(r,["value"]);const s=r.getAttribute("value");if(!s)return;const o=r.innerHTML;e.inputOptions[s]=o})),e},mw=(n,e)=>{const t={};for(const i in e){const r=e[i],s=n.querySelector(r);s&&(gr(s,[]),t[r.replace(/^swal-/,"")]=s.innerHTML.trim())}return t},gw=n=>{const e=Np.concat(["swal-param","swal-function-param","swal-button","swal-image","swal-icon","swal-input","swal-input-option"]);Array.from(n.children).forEach(t=>{const i=t.tagName.toLowerCase();e.includes(i)||jt(`Unrecognized element <${i}>`)})},gr=(n,e)=>{Array.from(n.attributes).forEach(t=>{e.indexOf(t.name)===-1&&jt([`Unrecognized attribute "${t.name}" on <${n.tagName.toLowerCase()}>.`,`${e.length?`Allowed attributes are: ${e.join(", ")}`:"To set the value, use HTML within the element."}`])})},kp=10,_w=n=>{const e=Zt(),t=Ye();typeof n.willOpen=="function"&&n.willOpen(t),Me.eventEmitter.emit("willOpen",t);const r=window.getComputedStyle(document.body).overflowY;ww(e,t,n),setTimeout(()=>{vw(e,t)},kp),Iu()&&(xw(e,n.scrollbarPadding,r),tx()),!Na()&&!Me.previousActiveElement&&(Me.previousActiveElement=document.activeElement),typeof n.didOpen=="function"&&setTimeout(()=>n.didOpen(t)),Me.eventEmitter.emit("didOpen",t)},ya=n=>{const e=Ye();if(n.target!==e)return;const t=Zt();e.removeEventListener("animationend",ya),e.removeEventListener("transitionend",ya),t.style.overflowY="auto",Ln(t,X["no-transition"])},vw=(n,e)=>{ep(e)?(n.style.overflowY="hidden",e.addEventListener("animationend",ya),e.addEventListener("transitionend",ya)):n.style.overflowY="auto"},xw=(n,e,t)=>{nx(),e&&t!=="hidden"&&cx(t),setTimeout(()=>{n.scrollTop=0})},ww=(n,e,t)=>{je(n,t.showClass.backdrop),t.animation?(e.style.setProperty("opacity","0","important"),Ut(e,"grid"),setTimeout(()=>{je(e,t.showClass.popup),e.style.removeProperty("opacity")},kp)):Ut(e,"grid"),je([document.documentElement,document.body],X.shown),t.heightAuto&&t.backdrop&&!t.toast&&je([document.documentElement,document.body],X["height-auto"])};var Kd={email:(n,e)=>/^[a-zA-Z0-9.+_'-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9-]+$/.test(n)?Promise.resolve():Promise.resolve(e||"Invalid email address"),url:(n,e)=>/^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-z]{2,63}\b([-a-zA-Z0-9@:%_+.~#?&/=]*)$/.test(n)?Promise.resolve():Promise.resolve(e||"Invalid URL")};function yw(n){n.inputValidator||(n.input==="email"&&(n.inputValidator=Kd.email),n.input==="url"&&(n.inputValidator=Kd.url))}function bw(n){(!n.target||typeof n.target=="string"&&!document.querySelector(n.target)||typeof n.target!="string"&&!n.target.appendChild)&&(jt('Target parameter is not valid, defaulting to "body"'),n.target="body")}function Sw(n){yw(n),n.showLoaderOnConfirm&&!n.preConfirm&&jt(`showLoaderOnConfirm is set to true, but preConfirm is not defined.
showLoaderOnConfirm should be used together with preConfirm, see usage example:
https://sweetalert2.github.io/#ajax-request`),bw(n),typeof n.title=="string"&&(n.title=n.title.split(`
`).join("<br />")),f0(n)}let Vn;var Eo=new WeakMap;class bt{constructor(...e){if(Wv(this,Eo,void 0),typeof window>"u")return;Vn=this;const t=Object.freeze(this.constructor.argsToParams(e));this.params=t,this.isAwaitingPromise=!1,Xv(Eo,this,this._main(Vn.params))}_main(e,t={}){if(Dp(Object.assign({},t,e)),Me.currentInstance){const s=is.swalPromiseResolve.get(Me.currentInstance),{isAwaitingPromise:o}=Me.currentInstance;Me.currentInstance._destroy(),o||s({isDismissed:!0}),Iu()&&hp()}Me.currentInstance=Vn;const i=Mw(e,t);Sw(i),Object.freeze(i),Me.timeout&&(Me.timeout.stop(),delete Me.timeout),clearTimeout(Me.restoreFocusTimeout);const r=Tw(Vn);return lp(Vn,i),ot.innerParams.set(Vn,i),Ew(Vn,r,i)}then(e){return zd(Eo,this).then(e)}finally(e){return zd(Eo,this).finally(e)}}const Ew=(n,e,t)=>new Promise((i,r)=>{const s=o=>{n.close({isDismissed:!0,dismiss:o,isConfirmed:!1,isDenied:!1})};is.swalPromiseResolve.set(n,i),is.swalPromiseReject.set(n,r),e.confirmButton.onclick=()=>{Tx(n)},e.denyButton.onclick=()=>{Ax(n)},e.cancelButton.onclick=()=>{Cx(n,s)},e.closeButton.onclick=()=>{s(ys.close)},zx(t,e,s),Y0(Me,t,s),_x(n,t),_w(t),Aw(Me,t,s),Cw(e,t),setTimeout(()=>{e.container.scrollTop=0})}),Mw=(n,e)=>{const t=lw(n),i=Object.assign({},jr,e,t,n);return i.showClass=Object.assign({},jr.showClass,i.showClass),i.hideClass=Object.assign({},jr.hideClass,i.hideClass),i.animation===!1&&(i.showClass={backdrop:"swal2-noanimation"},i.hideClass={}),i},Tw=n=>{const e={popup:Ye(),container:Zt(),actions:ho(),confirmButton:ei(),denyButton:Sr(),cancelButton:xs(),loader:ws(),closeButton:Du(),validationMessage:Oa(),progressSteps:Ru()};return ot.domCache.set(n,e),e},Aw=(n,e,t)=>{const i=Fa();Ht(i),e.timer&&(n.timeout=new aw(()=>{t("timer"),delete n.timeout},e.timer),e.timerProgressBar&&(Ut(i),_n(i,e,"timerProgressBar"),setTimeout(()=>{n.timeout&&n.timeout.running&&Ou(e.timer)})))},Cw=(n,e)=>{if(!e.toast){if(!Ua(e.allowEnterKey)){Yf("allowEnterKey"),Dw();return}Pw(n)||Rw(n,e)||oc(-1,1)}},Pw=n=>{const e=Array.from(n.popup.querySelectorAll("[autofocus]"));for(const t of e)if(t instanceof HTMLElement&&en(t))return t.focus(),!0;return!1},Rw=(n,e)=>e.focusDeny&&en(n.denyButton)?(n.denyButton.focus(),!0):e.focusCancel&&en(n.cancelButton)?(n.cancelButton.focus(),!0):e.focusConfirm&&en(n.confirmButton)?(n.confirmButton.focus(),!0):!1,Dw=()=>{document.activeElement instanceof HTMLElement&&typeof document.activeElement.blur=="function"&&document.activeElement.blur()};bt.prototype.disableButtons=Sp;bt.prototype.enableButtons=bp;bt.prototype.getInput=xp;bt.prototype.disableInput=Mp;bt.prototype.enableInput=Ep;bt.prototype.hideLoading=xa;bt.prototype.disableLoading=xa;bt.prototype.showValidationMessage=Tp;bt.prototype.resetValidationMessage=Ap;bt.prototype.close=Li;bt.prototype.closePopup=Li;bt.prototype.closeModal=Li;bt.prototype.closeToast=Li;bt.prototype.rejectPromise=mp;bt.prototype.update=Lp;bt.prototype._destroy=Ip;Object.assign(bt,ow);Object.keys(Bx).forEach(n=>{bt[n]=function(...e){return Vn&&Vn[n]?Vn[n](...e):null}});bt.DismissReason=ys;bt.version="11.26.3";const Xs=bt;Xs.default=Xs;typeof document<"u"&&(function(n,e){var t=n.createElement("style");if(n.getElementsByTagName("head")[0].appendChild(t),t.styleSheet)t.styleSheet.disabled||(t.styleSheet.cssText=e);else try{t.innerHTML=e}catch{t.innerText=e}})(document,':root{--swal2-outline: 0 0 0 3px rgba(100, 150, 200, 0.5);--swal2-container-padding: 0.625em;--swal2-backdrop: rgba(0, 0, 0, 0.4);--swal2-backdrop-transition: background-color 0.15s;--swal2-width: 32em;--swal2-padding: 0 0 1.25em;--swal2-border: none;--swal2-border-radius: 0.3125rem;--swal2-background: white;--swal2-color: #545454;--swal2-show-animation: swal2-show 0.3s;--swal2-hide-animation: swal2-hide 0.15s forwards;--swal2-icon-zoom: 1;--swal2-icon-animations: true;--swal2-title-padding: 0.8em 1em 0;--swal2-html-container-padding: 1em 1.6em 0.3em;--swal2-input-border: 1px solid #d9d9d9;--swal2-input-border-radius: 0.1875em;--swal2-input-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.06), 0 0 0 3px transparent;--swal2-input-background: transparent;--swal2-input-transition: border-color 0.2s, box-shadow 0.2s;--swal2-input-hover-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.06), 0 0 0 3px transparent;--swal2-input-focus-border: 1px solid #b4dbed;--swal2-input-focus-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.06), 0 0 0 3px rgba(100, 150, 200, 0.5);--swal2-progress-step-background: #add8e6;--swal2-validation-message-background: #f0f0f0;--swal2-validation-message-color: #666;--swal2-footer-border-color: #eee;--swal2-footer-background: transparent;--swal2-footer-color: inherit;--swal2-timer-progress-bar-background: rgba(0, 0, 0, 0.3);--swal2-close-button-position: initial;--swal2-close-button-inset: auto;--swal2-close-button-font-size: 2.5em;--swal2-close-button-color: #ccc;--swal2-close-button-transition: color 0.2s, box-shadow 0.2s;--swal2-close-button-outline: initial;--swal2-close-button-box-shadow: inset 0 0 0 3px transparent;--swal2-close-button-focus-box-shadow: inset var(--swal2-outline);--swal2-close-button-hover-transform: none;--swal2-actions-justify-content: center;--swal2-actions-width: auto;--swal2-actions-margin: 1.25em auto 0;--swal2-actions-padding: 0;--swal2-actions-border-radius: 0;--swal2-actions-background: transparent;--swal2-action-button-transition: background-color 0.2s, box-shadow 0.2s;--swal2-action-button-hover: black 10%;--swal2-action-button-active: black 10%;--swal2-confirm-button-box-shadow: none;--swal2-confirm-button-border-radius: 0.25em;--swal2-confirm-button-background-color: #7066e0;--swal2-confirm-button-color: #fff;--swal2-deny-button-box-shadow: none;--swal2-deny-button-border-radius: 0.25em;--swal2-deny-button-background-color: #dc3741;--swal2-deny-button-color: #fff;--swal2-cancel-button-box-shadow: none;--swal2-cancel-button-border-radius: 0.25em;--swal2-cancel-button-background-color: #6e7881;--swal2-cancel-button-color: #fff;--swal2-toast-show-animation: swal2-toast-show 0.5s;--swal2-toast-hide-animation: swal2-toast-hide 0.1s forwards;--swal2-toast-border: none;--swal2-toast-box-shadow: 0 0 1px hsl(0deg 0% 0% / 0.075), 0 1px 2px hsl(0deg 0% 0% / 0.075), 1px 2px 4px hsl(0deg 0% 0% / 0.075), 1px 3px 8px hsl(0deg 0% 0% / 0.075), 2px 4px 16px hsl(0deg 0% 0% / 0.075)}[data-swal2-theme=dark]{--swal2-dark-theme-black: #19191a;--swal2-dark-theme-white: #e1e1e1;--swal2-background: var(--swal2-dark-theme-black);--swal2-color: var(--swal2-dark-theme-white);--swal2-footer-border-color: #555;--swal2-input-background: color-mix(in srgb, var(--swal2-dark-theme-black), var(--swal2-dark-theme-white) 10%);--swal2-validation-message-background: color-mix( in srgb, var(--swal2-dark-theme-black), var(--swal2-dark-theme-white) 10% );--swal2-validation-message-color: var(--swal2-dark-theme-white);--swal2-timer-progress-bar-background: rgba(255, 255, 255, 0.7)}@media(prefers-color-scheme: dark){[data-swal2-theme=auto]{--swal2-dark-theme-black: #19191a;--swal2-dark-theme-white: #e1e1e1;--swal2-background: var(--swal2-dark-theme-black);--swal2-color: var(--swal2-dark-theme-white);--swal2-footer-border-color: #555;--swal2-input-background: color-mix(in srgb, var(--swal2-dark-theme-black), var(--swal2-dark-theme-white) 10%);--swal2-validation-message-background: color-mix( in srgb, var(--swal2-dark-theme-black), var(--swal2-dark-theme-white) 10% );--swal2-validation-message-color: var(--swal2-dark-theme-white);--swal2-timer-progress-bar-background: rgba(255, 255, 255, 0.7)}}body.swal2-shown:not(.swal2-no-backdrop,.swal2-toast-shown){overflow:hidden}body.swal2-height-auto{height:auto !important}body.swal2-no-backdrop .swal2-container{background-color:rgba(0,0,0,0) !important;pointer-events:none}body.swal2-no-backdrop .swal2-container .swal2-popup{pointer-events:all}body.swal2-no-backdrop .swal2-container .swal2-modal{box-shadow:0 0 10px var(--swal2-backdrop)}body.swal2-toast-shown .swal2-container{box-sizing:border-box;width:360px;max-width:100%;background-color:rgba(0,0,0,0);pointer-events:none}body.swal2-toast-shown .swal2-container.swal2-top{inset:0 auto auto 50%;transform:translateX(-50%)}body.swal2-toast-shown .swal2-container.swal2-top-end,body.swal2-toast-shown .swal2-container.swal2-top-right{inset:0 0 auto auto}body.swal2-toast-shown .swal2-container.swal2-top-start,body.swal2-toast-shown .swal2-container.swal2-top-left{inset:0 auto auto 0}body.swal2-toast-shown .swal2-container.swal2-center-start,body.swal2-toast-shown .swal2-container.swal2-center-left{inset:50% auto auto 0;transform:translateY(-50%)}body.swal2-toast-shown .swal2-container.swal2-center{inset:50% auto auto 50%;transform:translate(-50%, -50%)}body.swal2-toast-shown .swal2-container.swal2-center-end,body.swal2-toast-shown .swal2-container.swal2-center-right{inset:50% 0 auto auto;transform:translateY(-50%)}body.swal2-toast-shown .swal2-container.swal2-bottom-start,body.swal2-toast-shown .swal2-container.swal2-bottom-left{inset:auto auto 0 0}body.swal2-toast-shown .swal2-container.swal2-bottom{inset:auto auto 0 50%;transform:translateX(-50%)}body.swal2-toast-shown .swal2-container.swal2-bottom-end,body.swal2-toast-shown .swal2-container.swal2-bottom-right{inset:auto 0 0 auto}@media print{body.swal2-shown:not(.swal2-no-backdrop,.swal2-toast-shown){overflow-y:scroll !important}body.swal2-shown:not(.swal2-no-backdrop,.swal2-toast-shown)>[aria-hidden=true]{display:none}body.swal2-shown:not(.swal2-no-backdrop,.swal2-toast-shown) .swal2-container{position:static !important}}div:where(.swal2-container){display:grid;position:fixed;z-index:1060;inset:0;box-sizing:border-box;grid-template-areas:"top-start     top            top-end" "center-start  center         center-end" "bottom-start  bottom-center  bottom-end";grid-template-rows:minmax(min-content, auto) minmax(min-content, auto) minmax(min-content, auto);height:100%;padding:var(--swal2-container-padding);overflow-x:hidden;transition:var(--swal2-backdrop-transition);-webkit-overflow-scrolling:touch}div:where(.swal2-container).swal2-backdrop-show,div:where(.swal2-container).swal2-noanimation{background:var(--swal2-backdrop)}div:where(.swal2-container).swal2-backdrop-hide{background:rgba(0,0,0,0) !important}div:where(.swal2-container).swal2-top-start,div:where(.swal2-container).swal2-center-start,div:where(.swal2-container).swal2-bottom-start{grid-template-columns:minmax(0, 1fr) auto auto}div:where(.swal2-container).swal2-top,div:where(.swal2-container).swal2-center,div:where(.swal2-container).swal2-bottom{grid-template-columns:auto minmax(0, 1fr) auto}div:where(.swal2-container).swal2-top-end,div:where(.swal2-container).swal2-center-end,div:where(.swal2-container).swal2-bottom-end{grid-template-columns:auto auto minmax(0, 1fr)}div:where(.swal2-container).swal2-top-start>.swal2-popup{align-self:start}div:where(.swal2-container).swal2-top>.swal2-popup{grid-column:2;place-self:start center}div:where(.swal2-container).swal2-top-end>.swal2-popup,div:where(.swal2-container).swal2-top-right>.swal2-popup{grid-column:3;place-self:start end}div:where(.swal2-container).swal2-center-start>.swal2-popup,div:where(.swal2-container).swal2-center-left>.swal2-popup{grid-row:2;align-self:center}div:where(.swal2-container).swal2-center>.swal2-popup{grid-column:2;grid-row:2;place-self:center center}div:where(.swal2-container).swal2-center-end>.swal2-popup,div:where(.swal2-container).swal2-center-right>.swal2-popup{grid-column:3;grid-row:2;place-self:center end}div:where(.swal2-container).swal2-bottom-start>.swal2-popup,div:where(.swal2-container).swal2-bottom-left>.swal2-popup{grid-column:1;grid-row:3;align-self:end}div:where(.swal2-container).swal2-bottom>.swal2-popup{grid-column:2;grid-row:3;place-self:end center}div:where(.swal2-container).swal2-bottom-end>.swal2-popup,div:where(.swal2-container).swal2-bottom-right>.swal2-popup{grid-column:3;grid-row:3;place-self:end end}div:where(.swal2-container).swal2-grow-row>.swal2-popup,div:where(.swal2-container).swal2-grow-fullscreen>.swal2-popup{grid-column:1/4;width:100%}div:where(.swal2-container).swal2-grow-column>.swal2-popup,div:where(.swal2-container).swal2-grow-fullscreen>.swal2-popup{grid-row:1/4;align-self:stretch}div:where(.swal2-container).swal2-no-transition{transition:none !important}div:where(.swal2-container)[popover]{width:auto;border:0}div:where(.swal2-container) div:where(.swal2-popup){display:none;position:relative;box-sizing:border-box;grid-template-columns:minmax(0, 100%);width:var(--swal2-width);max-width:100%;padding:var(--swal2-padding);border:var(--swal2-border);border-radius:var(--swal2-border-radius);background:var(--swal2-background);color:var(--swal2-color);font-family:inherit;font-size:1rem;container-name:swal2-popup}div:where(.swal2-container) div:where(.swal2-popup):focus{outline:none}div:where(.swal2-container) div:where(.swal2-popup).swal2-loading{overflow-y:hidden}div:where(.swal2-container) div:where(.swal2-popup).swal2-draggable{cursor:grab}div:where(.swal2-container) div:where(.swal2-popup).swal2-draggable div:where(.swal2-icon){cursor:grab}div:where(.swal2-container) div:where(.swal2-popup).swal2-dragging{cursor:grabbing}div:where(.swal2-container) div:where(.swal2-popup).swal2-dragging div:where(.swal2-icon){cursor:grabbing}div:where(.swal2-container) h2:where(.swal2-title){position:relative;max-width:100%;margin:0;padding:var(--swal2-title-padding);color:inherit;font-size:1.875em;font-weight:600;text-align:center;text-transform:none;overflow-wrap:break-word;cursor:initial}div:where(.swal2-container) div:where(.swal2-actions){display:flex;z-index:1;box-sizing:border-box;flex-wrap:wrap;align-items:center;justify-content:var(--swal2-actions-justify-content);width:var(--swal2-actions-width);margin:var(--swal2-actions-margin);padding:var(--swal2-actions-padding);border-radius:var(--swal2-actions-border-radius);background:var(--swal2-actions-background)}div:where(.swal2-container) div:where(.swal2-loader){display:none;align-items:center;justify-content:center;width:2.2em;height:2.2em;margin:0 1.875em;animation:swal2-rotate-loading 1.5s linear 0s infinite normal;border-width:.25em;border-style:solid;border-radius:100%;border-color:#2778c4 rgba(0,0,0,0) #2778c4 rgba(0,0,0,0)}div:where(.swal2-container) button:where(.swal2-styled){margin:.3125em;padding:.625em 1.1em;transition:var(--swal2-action-button-transition);border:none;box-shadow:0 0 0 3px rgba(0,0,0,0);font-weight:500}div:where(.swal2-container) button:where(.swal2-styled):not([disabled]){cursor:pointer}div:where(.swal2-container) button:where(.swal2-styled):where(.swal2-confirm){border-radius:var(--swal2-confirm-button-border-radius);background:initial;background-color:var(--swal2-confirm-button-background-color);box-shadow:var(--swal2-confirm-button-box-shadow);color:var(--swal2-confirm-button-color);font-size:1em}div:where(.swal2-container) button:where(.swal2-styled):where(.swal2-confirm):hover{background-color:color-mix(in srgb, var(--swal2-confirm-button-background-color), var(--swal2-action-button-hover))}div:where(.swal2-container) button:where(.swal2-styled):where(.swal2-confirm):active{background-color:color-mix(in srgb, var(--swal2-confirm-button-background-color), var(--swal2-action-button-active))}div:where(.swal2-container) button:where(.swal2-styled):where(.swal2-deny){border-radius:var(--swal2-deny-button-border-radius);background:initial;background-color:var(--swal2-deny-button-background-color);box-shadow:var(--swal2-deny-button-box-shadow);color:var(--swal2-deny-button-color);font-size:1em}div:where(.swal2-container) button:where(.swal2-styled):where(.swal2-deny):hover{background-color:color-mix(in srgb, var(--swal2-deny-button-background-color), var(--swal2-action-button-hover))}div:where(.swal2-container) button:where(.swal2-styled):where(.swal2-deny):active{background-color:color-mix(in srgb, var(--swal2-deny-button-background-color), var(--swal2-action-button-active))}div:where(.swal2-container) button:where(.swal2-styled):where(.swal2-cancel){border-radius:var(--swal2-cancel-button-border-radius);background:initial;background-color:var(--swal2-cancel-button-background-color);box-shadow:var(--swal2-cancel-button-box-shadow);color:var(--swal2-cancel-button-color);font-size:1em}div:where(.swal2-container) button:where(.swal2-styled):where(.swal2-cancel):hover{background-color:color-mix(in srgb, var(--swal2-cancel-button-background-color), var(--swal2-action-button-hover))}div:where(.swal2-container) button:where(.swal2-styled):where(.swal2-cancel):active{background-color:color-mix(in srgb, var(--swal2-cancel-button-background-color), var(--swal2-action-button-active))}div:where(.swal2-container) button:where(.swal2-styled):focus-visible{outline:none;box-shadow:var(--swal2-action-button-focus-box-shadow)}div:where(.swal2-container) button:where(.swal2-styled)[disabled]:not(.swal2-loading){opacity:.4}div:where(.swal2-container) button:where(.swal2-styled)::-moz-focus-inner{border:0}div:where(.swal2-container) div:where(.swal2-footer){margin:1em 0 0;padding:1em 1em 0;border-top:1px solid var(--swal2-footer-border-color);background:var(--swal2-footer-background);color:var(--swal2-footer-color);font-size:1em;text-align:center;cursor:initial}div:where(.swal2-container) .swal2-timer-progress-bar-container{position:absolute;right:0;bottom:0;left:0;grid-column:auto !important;overflow:hidden;border-bottom-right-radius:var(--swal2-border-radius);border-bottom-left-radius:var(--swal2-border-radius)}div:where(.swal2-container) div:where(.swal2-timer-progress-bar){width:100%;height:.25em;background:var(--swal2-timer-progress-bar-background)}div:where(.swal2-container) img:where(.swal2-image){max-width:100%;margin:2em auto 1em;cursor:initial}div:where(.swal2-container) button:where(.swal2-close){position:var(--swal2-close-button-position);inset:var(--swal2-close-button-inset);z-index:2;align-items:center;justify-content:center;width:1.2em;height:1.2em;margin-top:0;margin-right:0;margin-bottom:-1.2em;padding:0;overflow:hidden;transition:var(--swal2-close-button-transition);border:none;border-radius:var(--swal2-border-radius);outline:var(--swal2-close-button-outline);background:rgba(0,0,0,0);color:var(--swal2-close-button-color);font-family:monospace;font-size:var(--swal2-close-button-font-size);cursor:pointer;justify-self:end}div:where(.swal2-container) button:where(.swal2-close):hover{transform:var(--swal2-close-button-hover-transform);background:rgba(0,0,0,0);color:#f27474}div:where(.swal2-container) button:where(.swal2-close):focus-visible{outline:none;box-shadow:var(--swal2-close-button-focus-box-shadow)}div:where(.swal2-container) button:where(.swal2-close)::-moz-focus-inner{border:0}div:where(.swal2-container) div:where(.swal2-html-container){z-index:1;justify-content:center;margin:0;padding:var(--swal2-html-container-padding);overflow:auto;color:inherit;font-size:1.125em;font-weight:normal;line-height:normal;text-align:center;overflow-wrap:break-word;word-break:break-word;cursor:initial}div:where(.swal2-container) input:where(.swal2-input),div:where(.swal2-container) input:where(.swal2-file),div:where(.swal2-container) textarea:where(.swal2-textarea),div:where(.swal2-container) select:where(.swal2-select),div:where(.swal2-container) div:where(.swal2-radio),div:where(.swal2-container) label:where(.swal2-checkbox){margin:1em 2em 3px}div:where(.swal2-container) input:where(.swal2-input),div:where(.swal2-container) input:where(.swal2-file),div:where(.swal2-container) textarea:where(.swal2-textarea){box-sizing:border-box;width:auto;transition:var(--swal2-input-transition);border:var(--swal2-input-border);border-radius:var(--swal2-input-border-radius);background:var(--swal2-input-background);box-shadow:var(--swal2-input-box-shadow);color:inherit;font-size:1.125em}div:where(.swal2-container) input:where(.swal2-input).swal2-inputerror,div:where(.swal2-container) input:where(.swal2-file).swal2-inputerror,div:where(.swal2-container) textarea:where(.swal2-textarea).swal2-inputerror{border-color:#f27474 !important;box-shadow:0 0 2px #f27474 !important}div:where(.swal2-container) input:where(.swal2-input):hover,div:where(.swal2-container) input:where(.swal2-file):hover,div:where(.swal2-container) textarea:where(.swal2-textarea):hover{box-shadow:var(--swal2-input-hover-box-shadow)}div:where(.swal2-container) input:where(.swal2-input):focus,div:where(.swal2-container) input:where(.swal2-file):focus,div:where(.swal2-container) textarea:where(.swal2-textarea):focus{border:var(--swal2-input-focus-border);outline:none;box-shadow:var(--swal2-input-focus-box-shadow)}div:where(.swal2-container) input:where(.swal2-input)::placeholder,div:where(.swal2-container) input:where(.swal2-file)::placeholder,div:where(.swal2-container) textarea:where(.swal2-textarea)::placeholder{color:#ccc}div:where(.swal2-container) .swal2-range{margin:1em 2em 3px;background:var(--swal2-background)}div:where(.swal2-container) .swal2-range input{width:80%}div:where(.swal2-container) .swal2-range output{width:20%;color:inherit;font-weight:600;text-align:center}div:where(.swal2-container) .swal2-range input,div:where(.swal2-container) .swal2-range output{height:2.625em;padding:0;font-size:1.125em;line-height:2.625em}div:where(.swal2-container) .swal2-input{height:2.625em;padding:0 .75em}div:where(.swal2-container) .swal2-file{width:75%;margin-right:auto;margin-left:auto;background:var(--swal2-input-background);font-size:1.125em}div:where(.swal2-container) .swal2-textarea{height:6.75em;padding:.75em}div:where(.swal2-container) .swal2-select{min-width:50%;max-width:100%;padding:.375em .625em;background:var(--swal2-input-background);color:inherit;font-size:1.125em}div:where(.swal2-container) .swal2-radio,div:where(.swal2-container) .swal2-checkbox{align-items:center;justify-content:center;background:var(--swal2-background);color:inherit}div:where(.swal2-container) .swal2-radio label,div:where(.swal2-container) .swal2-checkbox label{margin:0 .6em;font-size:1.125em}div:where(.swal2-container) .swal2-radio input,div:where(.swal2-container) .swal2-checkbox input{flex-shrink:0;margin:0 .4em}div:where(.swal2-container) label:where(.swal2-input-label){display:flex;justify-content:center;margin:1em auto 0}div:where(.swal2-container) div:where(.swal2-validation-message){align-items:center;justify-content:center;margin:1em 0 0;padding:.625em;overflow:hidden;background:var(--swal2-validation-message-background);color:var(--swal2-validation-message-color);font-size:1em;font-weight:300}div:where(.swal2-container) div:where(.swal2-validation-message)::before{content:"!";display:inline-block;width:1.5em;min-width:1.5em;height:1.5em;margin:0 .625em;border-radius:50%;background-color:#f27474;color:#fff;font-weight:600;line-height:1.5em;text-align:center}div:where(.swal2-container) .swal2-progress-steps{flex-wrap:wrap;align-items:center;max-width:100%;margin:1.25em auto;padding:0;background:rgba(0,0,0,0);font-weight:600}div:where(.swal2-container) .swal2-progress-steps li{display:inline-block;position:relative}div:where(.swal2-container) .swal2-progress-steps .swal2-progress-step{z-index:20;flex-shrink:0;width:2em;height:2em;border-radius:2em;background:#2778c4;color:#fff;line-height:2em;text-align:center}div:where(.swal2-container) .swal2-progress-steps .swal2-progress-step.swal2-active-progress-step{background:#2778c4}div:where(.swal2-container) .swal2-progress-steps .swal2-progress-step.swal2-active-progress-step~.swal2-progress-step{background:var(--swal2-progress-step-background);color:#fff}div:where(.swal2-container) .swal2-progress-steps .swal2-progress-step.swal2-active-progress-step~.swal2-progress-step-line{background:var(--swal2-progress-step-background)}div:where(.swal2-container) .swal2-progress-steps .swal2-progress-step-line{z-index:10;flex-shrink:0;width:2.5em;height:.4em;margin:0 -1px;background:#2778c4}div:where(.swal2-icon){position:relative;box-sizing:content-box;justify-content:center;width:5em;height:5em;margin:2.5em auto .6em;zoom:var(--swal2-icon-zoom);border:.25em solid rgba(0,0,0,0);border-radius:50%;border-color:#000;font-family:inherit;line-height:5em;cursor:default;user-select:none}div:where(.swal2-icon) .swal2-icon-content{display:flex;align-items:center;font-size:3.75em}div:where(.swal2-icon).swal2-error{border-color:#f27474;color:#f27474}div:where(.swal2-icon).swal2-error .swal2-x-mark{position:relative;flex-grow:1}div:where(.swal2-icon).swal2-error [class^=swal2-x-mark-line]{display:block;position:absolute;top:2.3125em;width:2.9375em;height:.3125em;border-radius:.125em;background-color:#f27474}div:where(.swal2-icon).swal2-error [class^=swal2-x-mark-line][class$=left]{left:1.0625em;transform:rotate(45deg)}div:where(.swal2-icon).swal2-error [class^=swal2-x-mark-line][class$=right]{right:1em;transform:rotate(-45deg)}@container swal2-popup style(--swal2-icon-animations:true){div:where(.swal2-icon).swal2-error.swal2-icon-show{animation:swal2-animate-error-icon .5s}div:where(.swal2-icon).swal2-error.swal2-icon-show .swal2-x-mark{animation:swal2-animate-error-x-mark .5s}}div:where(.swal2-icon).swal2-warning{border-color:#f8bb86;color:#f8bb86}@container swal2-popup style(--swal2-icon-animations:true){div:where(.swal2-icon).swal2-warning.swal2-icon-show{animation:swal2-animate-error-icon .5s}div:where(.swal2-icon).swal2-warning.swal2-icon-show .swal2-icon-content{animation:swal2-animate-i-mark .5s}}div:where(.swal2-icon).swal2-info{border-color:#3fc3ee;color:#3fc3ee}@container swal2-popup style(--swal2-icon-animations:true){div:where(.swal2-icon).swal2-info.swal2-icon-show{animation:swal2-animate-error-icon .5s}div:where(.swal2-icon).swal2-info.swal2-icon-show .swal2-icon-content{animation:swal2-animate-i-mark .8s}}div:where(.swal2-icon).swal2-question{border-color:#87adbd;color:#87adbd}@container swal2-popup style(--swal2-icon-animations:true){div:where(.swal2-icon).swal2-question.swal2-icon-show{animation:swal2-animate-error-icon .5s}div:where(.swal2-icon).swal2-question.swal2-icon-show .swal2-icon-content{animation:swal2-animate-question-mark .8s}}div:where(.swal2-icon).swal2-success{border-color:#a5dc86;color:#a5dc86}div:where(.swal2-icon).swal2-success [class^=swal2-success-circular-line]{position:absolute;width:3.75em;height:7.5em;border-radius:50%}div:where(.swal2-icon).swal2-success [class^=swal2-success-circular-line][class$=left]{top:-0.4375em;left:-2.0635em;transform:rotate(-45deg);transform-origin:3.75em 3.75em;border-radius:7.5em 0 0 7.5em}div:where(.swal2-icon).swal2-success [class^=swal2-success-circular-line][class$=right]{top:-0.6875em;left:1.875em;transform:rotate(-45deg);transform-origin:0 3.75em;border-radius:0 7.5em 7.5em 0}div:where(.swal2-icon).swal2-success .swal2-success-ring{position:absolute;z-index:2;top:-0.25em;left:-0.25em;box-sizing:content-box;width:100%;height:100%;border:.25em solid rgba(165,220,134,.3);border-radius:50%}div:where(.swal2-icon).swal2-success .swal2-success-fix{position:absolute;z-index:1;top:.5em;left:1.625em;width:.4375em;height:5.625em;transform:rotate(-45deg)}div:where(.swal2-icon).swal2-success [class^=swal2-success-line]{display:block;position:absolute;z-index:2;height:.3125em;border-radius:.125em;background-color:#a5dc86}div:where(.swal2-icon).swal2-success [class^=swal2-success-line][class$=tip]{top:2.875em;left:.8125em;width:1.5625em;transform:rotate(45deg)}div:where(.swal2-icon).swal2-success [class^=swal2-success-line][class$=long]{top:2.375em;right:.5em;width:2.9375em;transform:rotate(-45deg)}@container swal2-popup style(--swal2-icon-animations:true){div:where(.swal2-icon).swal2-success.swal2-icon-show .swal2-success-line-tip{animation:swal2-animate-success-line-tip .75s}div:where(.swal2-icon).swal2-success.swal2-icon-show .swal2-success-line-long{animation:swal2-animate-success-line-long .75s}div:where(.swal2-icon).swal2-success.swal2-icon-show .swal2-success-circular-line-right{animation:swal2-rotate-success-circular-line 4.25s ease-in}}[class^=swal2]{-webkit-tap-highlight-color:rgba(0,0,0,0)}.swal2-show{animation:var(--swal2-show-animation)}.swal2-hide{animation:var(--swal2-hide-animation)}.swal2-noanimation{transition:none}.swal2-scrollbar-measure{position:absolute;top:-9999px;width:50px;height:50px;overflow:scroll}.swal2-rtl .swal2-close{margin-right:initial;margin-left:0}.swal2-rtl .swal2-timer-progress-bar{right:0;left:auto}.swal2-toast{box-sizing:border-box;grid-column:1/4 !important;grid-row:1/4 !important;grid-template-columns:min-content auto min-content;padding:1em;overflow-y:hidden;border:var(--swal2-toast-border);background:var(--swal2-background);box-shadow:var(--swal2-toast-box-shadow);pointer-events:all}.swal2-toast>*{grid-column:2}.swal2-toast h2:where(.swal2-title){margin:.5em 1em;padding:0;font-size:1em;text-align:initial}.swal2-toast .swal2-loading{justify-content:center}.swal2-toast input:where(.swal2-input){height:2em;margin:.5em;font-size:1em}.swal2-toast .swal2-validation-message{font-size:1em}.swal2-toast div:where(.swal2-footer){margin:.5em 0 0;padding:.5em 0 0;font-size:.8em}.swal2-toast button:where(.swal2-close){grid-column:3/3;grid-row:1/99;align-self:center;width:.8em;height:.8em;margin:0;font-size:2em}.swal2-toast div:where(.swal2-html-container){margin:.5em 1em;padding:0;overflow:initial;font-size:1em;text-align:initial}.swal2-toast div:where(.swal2-html-container):empty{padding:0}.swal2-toast .swal2-loader{grid-column:1;grid-row:1/99;align-self:center;width:2em;height:2em;margin:.25em}.swal2-toast .swal2-icon{grid-column:1;grid-row:1/99;align-self:center;width:2em;min-width:2em;height:2em;margin:0 .5em 0 0}.swal2-toast .swal2-icon .swal2-icon-content{display:flex;align-items:center;font-size:1.8em;font-weight:bold}.swal2-toast .swal2-icon.swal2-success .swal2-success-ring{width:2em;height:2em}.swal2-toast .swal2-icon.swal2-error [class^=swal2-x-mark-line]{top:.875em;width:1.375em}.swal2-toast .swal2-icon.swal2-error [class^=swal2-x-mark-line][class$=left]{left:.3125em}.swal2-toast .swal2-icon.swal2-error [class^=swal2-x-mark-line][class$=right]{right:.3125em}.swal2-toast div:where(.swal2-actions){justify-content:flex-start;height:auto;margin:0;margin-top:.5em;padding:0 .5em}.swal2-toast button:where(.swal2-styled){margin:.25em .5em;padding:.4em .6em;font-size:1em}.swal2-toast .swal2-success{border-color:#a5dc86}.swal2-toast .swal2-success [class^=swal2-success-circular-line]{position:absolute;width:1.6em;height:3em;border-radius:50%}.swal2-toast .swal2-success [class^=swal2-success-circular-line][class$=left]{top:-0.8em;left:-0.5em;transform:rotate(-45deg);transform-origin:2em 2em;border-radius:4em 0 0 4em}.swal2-toast .swal2-success [class^=swal2-success-circular-line][class$=right]{top:-0.25em;left:.9375em;transform-origin:0 1.5em;border-radius:0 4em 4em 0}.swal2-toast .swal2-success .swal2-success-ring{width:2em;height:2em}.swal2-toast .swal2-success .swal2-success-fix{top:0;left:.4375em;width:.4375em;height:2.6875em}.swal2-toast .swal2-success [class^=swal2-success-line]{height:.3125em}.swal2-toast .swal2-success [class^=swal2-success-line][class$=tip]{top:1.125em;left:.1875em;width:.75em}.swal2-toast .swal2-success [class^=swal2-success-line][class$=long]{top:.9375em;right:.1875em;width:1.375em}@container swal2-popup style(--swal2-icon-animations:true){.swal2-toast .swal2-success.swal2-icon-show .swal2-success-line-tip{animation:swal2-toast-animate-success-line-tip .75s}.swal2-toast .swal2-success.swal2-icon-show .swal2-success-line-long{animation:swal2-toast-animate-success-line-long .75s}}.swal2-toast.swal2-show{animation:var(--swal2-toast-show-animation)}.swal2-toast.swal2-hide{animation:var(--swal2-toast-hide-animation)}@keyframes swal2-show{0%{transform:translate3d(0, -50px, 0) scale(0.9);opacity:0}100%{transform:translate3d(0, 0, 0) scale(1);opacity:1}}@keyframes swal2-hide{0%{transform:translate3d(0, 0, 0) scale(1);opacity:1}100%{transform:translate3d(0, -50px, 0) scale(0.9);opacity:0}}@keyframes swal2-animate-success-line-tip{0%{top:1.1875em;left:.0625em;width:0}54%{top:1.0625em;left:.125em;width:0}70%{top:2.1875em;left:-0.375em;width:3.125em}84%{top:3em;left:1.3125em;width:1.0625em}100%{top:2.8125em;left:.8125em;width:1.5625em}}@keyframes swal2-animate-success-line-long{0%{top:3.375em;right:2.875em;width:0}65%{top:3.375em;right:2.875em;width:0}84%{top:2.1875em;right:0;width:3.4375em}100%{top:2.375em;right:.5em;width:2.9375em}}@keyframes swal2-rotate-success-circular-line{0%{transform:rotate(-45deg)}5%{transform:rotate(-45deg)}12%{transform:rotate(-405deg)}100%{transform:rotate(-405deg)}}@keyframes swal2-animate-error-x-mark{0%{margin-top:1.625em;transform:scale(0.4);opacity:0}50%{margin-top:1.625em;transform:scale(0.4);opacity:0}80%{margin-top:-0.375em;transform:scale(1.15)}100%{margin-top:0;transform:scale(1);opacity:1}}@keyframes swal2-animate-error-icon{0%{transform:rotateX(100deg);opacity:0}100%{transform:rotateX(0deg);opacity:1}}@keyframes swal2-rotate-loading{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}@keyframes swal2-animate-question-mark{0%{transform:rotateY(-360deg)}100%{transform:rotateY(0)}}@keyframes swal2-animate-i-mark{0%{transform:rotateZ(45deg);opacity:0}25%{transform:rotateZ(-25deg);opacity:.4}50%{transform:rotateZ(15deg);opacity:.8}75%{transform:rotateZ(-5deg);opacity:1}100%{transform:rotateX(0);opacity:1}}@keyframes swal2-toast-show{0%{transform:translateY(-0.625em) rotateZ(2deg)}33%{transform:translateY(0) rotateZ(-2deg)}66%{transform:translateY(0.3125em) rotateZ(2deg)}100%{transform:translateY(0) rotateZ(0deg)}}@keyframes swal2-toast-hide{100%{transform:rotateZ(1deg);opacity:0}}@keyframes swal2-toast-animate-success-line-tip{0%{top:.5625em;left:.0625em;width:0}54%{top:.125em;left:.125em;width:0}70%{top:.625em;left:-0.25em;width:1.625em}84%{top:1.0625em;left:.75em;width:.5em}100%{top:1.125em;left:.1875em;width:.75em}}@keyframes swal2-toast-animate-success-line-long{0%{top:1.625em;right:1.375em;width:0}65%{top:1.25em;right:.9375em;width:0}84%{top:.9375em;right:0;width:1.125em}100%{top:.9375em;right:.1875em;width:1.375em}}');/**
 * @license
 * Copyright 2010-2025 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const Vu="180",Kr={ROTATE:0,DOLLY:1,PAN:2},Wr={ROTATE:0,PAN:1,DOLLY_PAN:2,DOLLY_ROTATE:3},Lw=0,Zd=1,Iw=2,Bp=1,Uw=2,ci=3,Hi=0,qt=1,hi=2,ki=0,Zr=1,lc=2,Jd=3,Qd=4,Ow=5,sr=100,Fw=101,Nw=102,kw=103,Bw=104,zw=200,Vw=201,Hw=202,Gw=203,cc=204,uc=205,Ww=206,Xw=207,$w=208,qw=209,Yw=210,jw=211,Kw=212,Zw=213,Jw=214,dc=0,hc=1,fc=2,ss=3,pc=4,mc=5,gc=6,_c=7,zp=0,Qw=1,ey=2,Bi=0,ty=1,ny=2,iy=3,ry=4,sy=5,oy=6,ay=7,Vp=300,os=301,as=302,vc=303,xc=304,Ba=306,wc=1e3,lr=1001,yc=1002,kn=1003,ly=1004,Mo=1005,qn=1006,dl=1007,cr=1008,_i=1009,Hp=1010,Gp=1011,$s=1012,Hu=1013,_r=1014,fi=1015,go=1016,Gu=1017,Wu=1018,qs=1020,Wp=35902,Xp=35899,$p=1021,qp=1022,Nn=1023,Ys=1026,js=1027,Yp=1028,Xu=1029,jp=1030,$u=1031,qu=1033,Qo=33776,ea=33777,ta=33778,na=33779,bc=35840,Sc=35841,Ec=35842,Mc=35843,Tc=36196,Ac=37492,Cc=37496,Pc=37808,Rc=37809,Dc=37810,Lc=37811,Ic=37812,Uc=37813,Oc=37814,Fc=37815,Nc=37816,kc=37817,Bc=37818,zc=37819,Vc=37820,Hc=37821,Gc=36492,Wc=36494,Xc=36495,$c=36283,qc=36284,Yc=36285,jc=36286,cy=3200,uy=3201,dy=0,hy=1,Pi="",An="srgb",ls="srgb-linear",ba="linear",et="srgb",Ar=7680,eh=519,fy=512,py=513,my=514,Kp=515,gy=516,_y=517,vy=518,xy=519,th=35044,nh="300 es",Yn=2e3,Sa=2001;class Er{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const i=this._listeners;i[e]===void 0&&(i[e]=[]),i[e].indexOf(t)===-1&&i[e].push(t)}hasEventListener(e,t){const i=this._listeners;return i===void 0?!1:i[e]!==void 0&&i[e].indexOf(t)!==-1}removeEventListener(e,t){const i=this._listeners;if(i===void 0)return;const r=i[e];if(r!==void 0){const s=r.indexOf(t);s!==-1&&r.splice(s,1)}}dispatchEvent(e){const t=this._listeners;if(t===void 0)return;const i=t[e.type];if(i!==void 0){e.target=this;const r=i.slice(0);for(let s=0,o=r.length;s<o;s++)r[s].call(this,e);e.target=null}}}const kt=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let ih=1234567;const ks=Math.PI/180,Ks=180/Math.PI;function bs(){const n=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,i=Math.random()*4294967295|0;return(kt[n&255]+kt[n>>8&255]+kt[n>>16&255]+kt[n>>24&255]+"-"+kt[e&255]+kt[e>>8&255]+"-"+kt[e>>16&15|64]+kt[e>>24&255]+"-"+kt[t&63|128]+kt[t>>8&255]+"-"+kt[t>>16&255]+kt[t>>24&255]+kt[i&255]+kt[i>>8&255]+kt[i>>16&255]+kt[i>>24&255]).toLowerCase()}function Ve(n,e,t){return Math.max(e,Math.min(t,n))}function Yu(n,e){return(n%e+e)%e}function wy(n,e,t,i,r){return i+(n-e)*(r-i)/(t-e)}function yy(n,e,t){return n!==e?(t-n)/(e-n):0}function Bs(n,e,t){return(1-t)*n+t*e}function by(n,e,t,i){return Bs(n,e,1-Math.exp(-t*i))}function Sy(n,e=1){return e-Math.abs(Yu(n,e*2)-e)}function Ey(n,e,t){return n<=e?0:n>=t?1:(n=(n-e)/(t-e),n*n*(3-2*n))}function My(n,e,t){return n<=e?0:n>=t?1:(n=(n-e)/(t-e),n*n*n*(n*(n*6-15)+10))}function Ty(n,e){return n+Math.floor(Math.random()*(e-n+1))}function Ay(n,e){return n+Math.random()*(e-n)}function Cy(n){return n*(.5-Math.random())}function Py(n){n!==void 0&&(ih=n);let e=ih+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function Ry(n){return n*ks}function Dy(n){return n*Ks}function Ly(n){return(n&n-1)===0&&n!==0}function Iy(n){return Math.pow(2,Math.ceil(Math.log(n)/Math.LN2))}function Uy(n){return Math.pow(2,Math.floor(Math.log(n)/Math.LN2))}function Oy(n,e,t,i,r){const s=Math.cos,o=Math.sin,a=s(t/2),l=o(t/2),c=s((e+i)/2),u=o((e+i)/2),d=s((e-i)/2),p=o((e-i)/2),f=s((i-e)/2),_=o((i-e)/2);switch(r){case"XYX":n.set(a*u,l*d,l*p,a*c);break;case"YZY":n.set(l*p,a*u,l*d,a*c);break;case"ZXZ":n.set(l*d,l*p,a*u,a*c);break;case"XZX":n.set(a*u,l*_,l*f,a*c);break;case"YXY":n.set(l*f,a*u,l*_,a*c);break;case"ZYZ":n.set(l*_,l*f,a*u,a*c);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+r)}}function Gr(n,e){switch(e.constructor){case Float32Array:return n;case Uint32Array:return n/4294967295;case Uint16Array:return n/65535;case Uint8Array:return n/255;case Int32Array:return Math.max(n/2147483647,-1);case Int16Array:return Math.max(n/32767,-1);case Int8Array:return Math.max(n/127,-1);default:throw new Error("Invalid component type.")}}function Wt(n,e){switch(e.constructor){case Float32Array:return n;case Uint32Array:return Math.round(n*4294967295);case Uint16Array:return Math.round(n*65535);case Uint8Array:return Math.round(n*255);case Int32Array:return Math.round(n*2147483647);case Int16Array:return Math.round(n*32767);case Int8Array:return Math.round(n*127);default:throw new Error("Invalid component type.")}}const Kc={DEG2RAD:ks,RAD2DEG:Ks,generateUUID:bs,clamp:Ve,euclideanModulo:Yu,mapLinear:wy,inverseLerp:yy,lerp:Bs,damp:by,pingpong:Sy,smoothstep:Ey,smootherstep:My,randInt:Ty,randFloat:Ay,randFloatSpread:Cy,seededRandom:Py,degToRad:Ry,radToDeg:Dy,isPowerOfTwo:Ly,ceilPowerOfTwo:Iy,floorPowerOfTwo:Uy,setQuaternionFromProperEuler:Oy,normalize:Wt,denormalize:Gr};class Be{constructor(e=0,t=0){Be.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,i=this.y,r=e.elements;return this.x=r[0]*t+r[3]*i+r[6],this.y=r[1]*t+r[4]*i+r[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Ve(this.x,e.x,t.x),this.y=Ve(this.y,e.y,t.y),this}clampScalar(e,t){return this.x=Ve(this.x,e,t),this.y=Ve(this.y,e,t),this}clampLength(e,t){const i=this.length();return this.divideScalar(i||1).multiplyScalar(Ve(i,e,t))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const i=this.dot(e)/t;return Math.acos(Ve(i,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,i=this.y-e.y;return t*t+i*i}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,i){return this.x=e.x+(t.x-e.x)*i,this.y=e.y+(t.y-e.y)*i,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const i=Math.cos(t),r=Math.sin(t),s=this.x-e.x,o=this.y-e.y;return this.x=s*i-o*r+e.x,this.y=s*r+o*i+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class vr{constructor(e=0,t=0,i=0,r=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=i,this._w=r}static slerpFlat(e,t,i,r,s,o,a){let l=i[r+0],c=i[r+1],u=i[r+2],d=i[r+3];const p=s[o+0],f=s[o+1],_=s[o+2],g=s[o+3];if(a===0){e[t+0]=l,e[t+1]=c,e[t+2]=u,e[t+3]=d;return}if(a===1){e[t+0]=p,e[t+1]=f,e[t+2]=_,e[t+3]=g;return}if(d!==g||l!==p||c!==f||u!==_){let m=1-a;const h=l*p+c*f+u*_+d*g,v=h>=0?1:-1,x=1-h*h;if(x>Number.EPSILON){const S=Math.sqrt(x),C=Math.atan2(S,h*v);m=Math.sin(m*C)/S,a=Math.sin(a*C)/S}const w=a*v;if(l=l*m+p*w,c=c*m+f*w,u=u*m+_*w,d=d*m+g*w,m===1-a){const S=1/Math.sqrt(l*l+c*c+u*u+d*d);l*=S,c*=S,u*=S,d*=S}}e[t]=l,e[t+1]=c,e[t+2]=u,e[t+3]=d}static multiplyQuaternionsFlat(e,t,i,r,s,o){const a=i[r],l=i[r+1],c=i[r+2],u=i[r+3],d=s[o],p=s[o+1],f=s[o+2],_=s[o+3];return e[t]=a*_+u*d+l*f-c*p,e[t+1]=l*_+u*p+c*d-a*f,e[t+2]=c*_+u*f+a*p-l*d,e[t+3]=u*_-a*d-l*p-c*f,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,i,r){return this._x=e,this._y=t,this._z=i,this._w=r,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const i=e._x,r=e._y,s=e._z,o=e._order,a=Math.cos,l=Math.sin,c=a(i/2),u=a(r/2),d=a(s/2),p=l(i/2),f=l(r/2),_=l(s/2);switch(o){case"XYZ":this._x=p*u*d+c*f*_,this._y=c*f*d-p*u*_,this._z=c*u*_+p*f*d,this._w=c*u*d-p*f*_;break;case"YXZ":this._x=p*u*d+c*f*_,this._y=c*f*d-p*u*_,this._z=c*u*_-p*f*d,this._w=c*u*d+p*f*_;break;case"ZXY":this._x=p*u*d-c*f*_,this._y=c*f*d+p*u*_,this._z=c*u*_+p*f*d,this._w=c*u*d-p*f*_;break;case"ZYX":this._x=p*u*d-c*f*_,this._y=c*f*d+p*u*_,this._z=c*u*_-p*f*d,this._w=c*u*d+p*f*_;break;case"YZX":this._x=p*u*d+c*f*_,this._y=c*f*d+p*u*_,this._z=c*u*_-p*f*d,this._w=c*u*d-p*f*_;break;case"XZY":this._x=p*u*d-c*f*_,this._y=c*f*d-p*u*_,this._z=c*u*_+p*f*d,this._w=c*u*d+p*f*_;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+o)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const i=t/2,r=Math.sin(i);return this._x=e.x*r,this._y=e.y*r,this._z=e.z*r,this._w=Math.cos(i),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,i=t[0],r=t[4],s=t[8],o=t[1],a=t[5],l=t[9],c=t[2],u=t[6],d=t[10],p=i+a+d;if(p>0){const f=.5/Math.sqrt(p+1);this._w=.25/f,this._x=(u-l)*f,this._y=(s-c)*f,this._z=(o-r)*f}else if(i>a&&i>d){const f=2*Math.sqrt(1+i-a-d);this._w=(u-l)/f,this._x=.25*f,this._y=(r+o)/f,this._z=(s+c)/f}else if(a>d){const f=2*Math.sqrt(1+a-i-d);this._w=(s-c)/f,this._x=(r+o)/f,this._y=.25*f,this._z=(l+u)/f}else{const f=2*Math.sqrt(1+d-i-a);this._w=(o-r)/f,this._x=(s+c)/f,this._y=(l+u)/f,this._z=.25*f}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let i=e.dot(t)+1;return i<1e-8?(i=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=i):(this._x=0,this._y=-e.z,this._z=e.y,this._w=i)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=i),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(Ve(this.dot(e),-1,1)))}rotateTowards(e,t){const i=this.angleTo(e);if(i===0)return this;const r=Math.min(1,t/i);return this.slerp(e,r),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const i=e._x,r=e._y,s=e._z,o=e._w,a=t._x,l=t._y,c=t._z,u=t._w;return this._x=i*u+o*a+r*c-s*l,this._y=r*u+o*l+s*a-i*c,this._z=s*u+o*c+i*l-r*a,this._w=o*u-i*a-r*l-s*c,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const i=this._x,r=this._y,s=this._z,o=this._w;let a=o*e._w+i*e._x+r*e._y+s*e._z;if(a<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,a=-a):this.copy(e),a>=1)return this._w=o,this._x=i,this._y=r,this._z=s,this;const l=1-a*a;if(l<=Number.EPSILON){const f=1-t;return this._w=f*o+t*this._w,this._x=f*i+t*this._x,this._y=f*r+t*this._y,this._z=f*s+t*this._z,this.normalize(),this}const c=Math.sqrt(l),u=Math.atan2(c,a),d=Math.sin((1-t)*u)/c,p=Math.sin(t*u)/c;return this._w=o*d+this._w*p,this._x=i*d+this._x*p,this._y=r*d+this._y*p,this._z=s*d+this._z*p,this._onChangeCallback(),this}slerpQuaternions(e,t,i){return this.copy(e).slerp(t,i)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),i=Math.random(),r=Math.sqrt(1-i),s=Math.sqrt(i);return this.set(r*Math.sin(e),r*Math.cos(e),s*Math.sin(t),s*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class B{constructor(e=0,t=0,i=0){B.prototype.isVector3=!0,this.x=e,this.y=t,this.z=i}set(e,t,i){return i===void 0&&(i=this.z),this.x=e,this.y=t,this.z=i,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(rh.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(rh.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,i=this.y,r=this.z,s=e.elements;return this.x=s[0]*t+s[3]*i+s[6]*r,this.y=s[1]*t+s[4]*i+s[7]*r,this.z=s[2]*t+s[5]*i+s[8]*r,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,i=this.y,r=this.z,s=e.elements,o=1/(s[3]*t+s[7]*i+s[11]*r+s[15]);return this.x=(s[0]*t+s[4]*i+s[8]*r+s[12])*o,this.y=(s[1]*t+s[5]*i+s[9]*r+s[13])*o,this.z=(s[2]*t+s[6]*i+s[10]*r+s[14])*o,this}applyQuaternion(e){const t=this.x,i=this.y,r=this.z,s=e.x,o=e.y,a=e.z,l=e.w,c=2*(o*r-a*i),u=2*(a*t-s*r),d=2*(s*i-o*t);return this.x=t+l*c+o*d-a*u,this.y=i+l*u+a*c-s*d,this.z=r+l*d+s*u-o*c,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,i=this.y,r=this.z,s=e.elements;return this.x=s[0]*t+s[4]*i+s[8]*r,this.y=s[1]*t+s[5]*i+s[9]*r,this.z=s[2]*t+s[6]*i+s[10]*r,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Ve(this.x,e.x,t.x),this.y=Ve(this.y,e.y,t.y),this.z=Ve(this.z,e.z,t.z),this}clampScalar(e,t){return this.x=Ve(this.x,e,t),this.y=Ve(this.y,e,t),this.z=Ve(this.z,e,t),this}clampLength(e,t){const i=this.length();return this.divideScalar(i||1).multiplyScalar(Ve(i,e,t))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,i){return this.x=e.x+(t.x-e.x)*i,this.y=e.y+(t.y-e.y)*i,this.z=e.z+(t.z-e.z)*i,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const i=e.x,r=e.y,s=e.z,o=t.x,a=t.y,l=t.z;return this.x=r*l-s*a,this.y=s*o-i*l,this.z=i*a-r*o,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const i=e.dot(this)/t;return this.copy(e).multiplyScalar(i)}projectOnPlane(e){return hl.copy(this).projectOnVector(e),this.sub(hl)}reflect(e){return this.sub(hl.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const i=this.dot(e)/t;return Math.acos(Ve(i,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,i=this.y-e.y,r=this.z-e.z;return t*t+i*i+r*r}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,i){const r=Math.sin(t)*e;return this.x=r*Math.sin(i),this.y=Math.cos(t)*e,this.z=r*Math.cos(i),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,i){return this.x=e*Math.sin(t),this.y=i,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),i=this.setFromMatrixColumn(e,1).length(),r=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=i,this.z=r,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,i=Math.sqrt(1-t*t);return this.x=i*Math.cos(e),this.y=t,this.z=i*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const hl=new B,rh=new vr;class Fe{constructor(e,t,i,r,s,o,a,l,c){Fe.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,i,r,s,o,a,l,c)}set(e,t,i,r,s,o,a,l,c){const u=this.elements;return u[0]=e,u[1]=r,u[2]=a,u[3]=t,u[4]=s,u[5]=l,u[6]=i,u[7]=o,u[8]=c,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,i=e.elements;return t[0]=i[0],t[1]=i[1],t[2]=i[2],t[3]=i[3],t[4]=i[4],t[5]=i[5],t[6]=i[6],t[7]=i[7],t[8]=i[8],this}extractBasis(e,t,i){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),i.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const i=e.elements,r=t.elements,s=this.elements,o=i[0],a=i[3],l=i[6],c=i[1],u=i[4],d=i[7],p=i[2],f=i[5],_=i[8],g=r[0],m=r[3],h=r[6],v=r[1],x=r[4],w=r[7],S=r[2],C=r[5],T=r[8];return s[0]=o*g+a*v+l*S,s[3]=o*m+a*x+l*C,s[6]=o*h+a*w+l*T,s[1]=c*g+u*v+d*S,s[4]=c*m+u*x+d*C,s[7]=c*h+u*w+d*T,s[2]=p*g+f*v+_*S,s[5]=p*m+f*x+_*C,s[8]=p*h+f*w+_*T,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],i=e[1],r=e[2],s=e[3],o=e[4],a=e[5],l=e[6],c=e[7],u=e[8];return t*o*u-t*a*c-i*s*u+i*a*l+r*s*c-r*o*l}invert(){const e=this.elements,t=e[0],i=e[1],r=e[2],s=e[3],o=e[4],a=e[5],l=e[6],c=e[7],u=e[8],d=u*o-a*c,p=a*l-u*s,f=c*s-o*l,_=t*d+i*p+r*f;if(_===0)return this.set(0,0,0,0,0,0,0,0,0);const g=1/_;return e[0]=d*g,e[1]=(r*c-u*i)*g,e[2]=(a*i-r*o)*g,e[3]=p*g,e[4]=(u*t-r*l)*g,e[5]=(r*s-a*t)*g,e[6]=f*g,e[7]=(i*l-c*t)*g,e[8]=(o*t-i*s)*g,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,i,r,s,o,a){const l=Math.cos(s),c=Math.sin(s);return this.set(i*l,i*c,-i*(l*o+c*a)+o+e,-r*c,r*l,-r*(-c*o+l*a)+a+t,0,0,1),this}scale(e,t){return this.premultiply(fl.makeScale(e,t)),this}rotate(e){return this.premultiply(fl.makeRotation(-e)),this}translate(e,t){return this.premultiply(fl.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),i=Math.sin(e);return this.set(t,-i,0,i,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,i=e.elements;for(let r=0;r<9;r++)if(t[r]!==i[r])return!1;return!0}fromArray(e,t=0){for(let i=0;i<9;i++)this.elements[i]=e[i+t];return this}toArray(e=[],t=0){const i=this.elements;return e[t]=i[0],e[t+1]=i[1],e[t+2]=i[2],e[t+3]=i[3],e[t+4]=i[4],e[t+5]=i[5],e[t+6]=i[6],e[t+7]=i[7],e[t+8]=i[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const fl=new Fe;function Zp(n){for(let e=n.length-1;e>=0;--e)if(n[e]>=65535)return!0;return!1}function Zs(n){return document.createElementNS("http://www.w3.org/1999/xhtml",n)}function Fy(){const n=Zs("canvas");return n.style.display="block",n}const sh={};function Js(n){n in sh||(sh[n]=!0,console.warn(n))}function Ny(n,e,t){return new Promise(function(i,r){function s(){switch(n.clientWaitSync(e,n.SYNC_FLUSH_COMMANDS_BIT,0)){case n.WAIT_FAILED:r();break;case n.TIMEOUT_EXPIRED:setTimeout(s,t);break;default:i()}}setTimeout(s,t)})}const oh=new Fe().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),ah=new Fe().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);function ky(){const n={enabled:!0,workingColorSpace:ls,spaces:{},convert:function(r,s,o){return this.enabled===!1||s===o||!s||!o||(this.spaces[s].transfer===et&&(r.r=gi(r.r),r.g=gi(r.g),r.b=gi(r.b)),this.spaces[s].primaries!==this.spaces[o].primaries&&(r.applyMatrix3(this.spaces[s].toXYZ),r.applyMatrix3(this.spaces[o].fromXYZ)),this.spaces[o].transfer===et&&(r.r=Jr(r.r),r.g=Jr(r.g),r.b=Jr(r.b))),r},workingToColorSpace:function(r,s){return this.convert(r,this.workingColorSpace,s)},colorSpaceToWorking:function(r,s){return this.convert(r,s,this.workingColorSpace)},getPrimaries:function(r){return this.spaces[r].primaries},getTransfer:function(r){return r===Pi?ba:this.spaces[r].transfer},getToneMappingMode:function(r){return this.spaces[r].outputColorSpaceConfig.toneMappingMode||"standard"},getLuminanceCoefficients:function(r,s=this.workingColorSpace){return r.fromArray(this.spaces[s].luminanceCoefficients)},define:function(r){Object.assign(this.spaces,r)},_getMatrix:function(r,s,o){return r.copy(this.spaces[s].toXYZ).multiply(this.spaces[o].fromXYZ)},_getDrawingBufferColorSpace:function(r){return this.spaces[r].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(r=this.workingColorSpace){return this.spaces[r].workingColorSpaceConfig.unpackColorSpace},fromWorkingColorSpace:function(r,s){return Js("THREE.ColorManagement: .fromWorkingColorSpace() has been renamed to .workingToColorSpace()."),n.workingToColorSpace(r,s)},toWorkingColorSpace:function(r,s){return Js("THREE.ColorManagement: .toWorkingColorSpace() has been renamed to .colorSpaceToWorking()."),n.colorSpaceToWorking(r,s)}},e=[.64,.33,.3,.6,.15,.06],t=[.2126,.7152,.0722],i=[.3127,.329];return n.define({[ls]:{primaries:e,whitePoint:i,transfer:ba,toXYZ:oh,fromXYZ:ah,luminanceCoefficients:t,workingColorSpaceConfig:{unpackColorSpace:An},outputColorSpaceConfig:{drawingBufferColorSpace:An}},[An]:{primaries:e,whitePoint:i,transfer:et,toXYZ:oh,fromXYZ:ah,luminanceCoefficients:t,outputColorSpaceConfig:{drawingBufferColorSpace:An}}}),n}const qe=ky();function gi(n){return n<.04045?n*.0773993808:Math.pow(n*.9478672986+.0521327014,2.4)}function Jr(n){return n<.0031308?n*12.92:1.055*Math.pow(n,.41666)-.055}let Cr;class By{static getDataURL(e,t="image/png"){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let i;if(e instanceof HTMLCanvasElement)i=e;else{Cr===void 0&&(Cr=Zs("canvas")),Cr.width=e.width,Cr.height=e.height;const r=Cr.getContext("2d");e instanceof ImageData?r.putImageData(e,0,0):r.drawImage(e,0,0,e.width,e.height),i=Cr}return i.toDataURL(t)}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=Zs("canvas");t.width=e.width,t.height=e.height;const i=t.getContext("2d");i.drawImage(e,0,0,e.width,e.height);const r=i.getImageData(0,0,e.width,e.height),s=r.data;for(let o=0;o<s.length;o++)s[o]=gi(s[o]/255)*255;return i.putImageData(r,0,0),t}else if(e.data){const t=e.data.slice(0);for(let i=0;i<t.length;i++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[i]=Math.floor(gi(t[i]/255)*255):t[i]=gi(t[i]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let zy=0;class ju{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:zy++}),this.uuid=bs(),this.data=e,this.dataReady=!0,this.version=0}getSize(e){const t=this.data;return typeof HTMLVideoElement<"u"&&t instanceof HTMLVideoElement?e.set(t.videoWidth,t.videoHeight,0):t instanceof VideoFrame?e.set(t.displayHeight,t.displayWidth,0):t!==null?e.set(t.width,t.height,t.depth||0):e.set(0,0,0),e}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const i={uuid:this.uuid,url:""},r=this.data;if(r!==null){let s;if(Array.isArray(r)){s=[];for(let o=0,a=r.length;o<a;o++)r[o].isDataTexture?s.push(pl(r[o].image)):s.push(pl(r[o]))}else s=pl(r);i.url=s}return t||(e.images[this.uuid]=i),i}}function pl(n){return typeof HTMLImageElement<"u"&&n instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&n instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&n instanceof ImageBitmap?By.getDataURL(n):n.data?{data:Array.from(n.data),width:n.width,height:n.height,type:n.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let Vy=0;const ml=new B;class Yt extends Er{constructor(e=Yt.DEFAULT_IMAGE,t=Yt.DEFAULT_MAPPING,i=lr,r=lr,s=qn,o=cr,a=Nn,l=_i,c=Yt.DEFAULT_ANISOTROPY,u=Pi){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:Vy++}),this.uuid=bs(),this.name="",this.source=new ju(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=i,this.wrapT=r,this.magFilter=s,this.minFilter=o,this.anisotropy=c,this.format=a,this.internalFormat=null,this.type=l,this.offset=new Be(0,0),this.repeat=new Be(1,1),this.center=new Be(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new Fe,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=u,this.userData={},this.updateRanges=[],this.version=0,this.onUpdate=null,this.renderTarget=null,this.isRenderTargetTexture=!1,this.isArrayTexture=!!(e&&e.depth&&e.depth>1),this.pmremVersion=0}get width(){return this.source.getSize(ml).x}get height(){return this.source.getSize(ml).y}get depth(){return this.source.getSize(ml).z}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.renderTarget=e.renderTarget,this.isRenderTargetTexture=e.isRenderTargetTexture,this.isArrayTexture=e.isArrayTexture,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}setValues(e){for(const t in e){const i=e[t];if(i===void 0){console.warn(`THREE.Texture.setValues(): parameter '${t}' has value of undefined.`);continue}const r=this[t];if(r===void 0){console.warn(`THREE.Texture.setValues(): property '${t}' does not exist.`);continue}r&&i&&r.isVector2&&i.isVector2||r&&i&&r.isVector3&&i.isVector3||r&&i&&r.isMatrix3&&i.isMatrix3?r.copy(i):this[t]=i}}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const i={metadata:{version:4.7,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(i.userData=this.userData),t||(e.textures[this.uuid]=i),i}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==Vp)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case wc:e.x=e.x-Math.floor(e.x);break;case lr:e.x=e.x<0?0:1;break;case yc:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case wc:e.y=e.y-Math.floor(e.y);break;case lr:e.y=e.y<0?0:1;break;case yc:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}Yt.DEFAULT_IMAGE=null;Yt.DEFAULT_MAPPING=Vp;Yt.DEFAULT_ANISOTROPY=1;class yt{constructor(e=0,t=0,i=0,r=1){yt.prototype.isVector4=!0,this.x=e,this.y=t,this.z=i,this.w=r}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,i,r){return this.x=e,this.y=t,this.z=i,this.w=r,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,i=this.y,r=this.z,s=this.w,o=e.elements;return this.x=o[0]*t+o[4]*i+o[8]*r+o[12]*s,this.y=o[1]*t+o[5]*i+o[9]*r+o[13]*s,this.z=o[2]*t+o[6]*i+o[10]*r+o[14]*s,this.w=o[3]*t+o[7]*i+o[11]*r+o[15]*s,this}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this.w/=e.w,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,i,r,s;const l=e.elements,c=l[0],u=l[4],d=l[8],p=l[1],f=l[5],_=l[9],g=l[2],m=l[6],h=l[10];if(Math.abs(u-p)<.01&&Math.abs(d-g)<.01&&Math.abs(_-m)<.01){if(Math.abs(u+p)<.1&&Math.abs(d+g)<.1&&Math.abs(_+m)<.1&&Math.abs(c+f+h-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const x=(c+1)/2,w=(f+1)/2,S=(h+1)/2,C=(u+p)/4,T=(d+g)/4,A=(_+m)/4;return x>w&&x>S?x<.01?(i=0,r=.707106781,s=.707106781):(i=Math.sqrt(x),r=C/i,s=T/i):w>S?w<.01?(i=.707106781,r=0,s=.707106781):(r=Math.sqrt(w),i=C/r,s=A/r):S<.01?(i=.707106781,r=.707106781,s=0):(s=Math.sqrt(S),i=T/s,r=A/s),this.set(i,r,s,t),this}let v=Math.sqrt((m-_)*(m-_)+(d-g)*(d-g)+(p-u)*(p-u));return Math.abs(v)<.001&&(v=1),this.x=(m-_)/v,this.y=(d-g)/v,this.z=(p-u)/v,this.w=Math.acos((c+f+h-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Ve(this.x,e.x,t.x),this.y=Ve(this.y,e.y,t.y),this.z=Ve(this.z,e.z,t.z),this.w=Ve(this.w,e.w,t.w),this}clampScalar(e,t){return this.x=Ve(this.x,e,t),this.y=Ve(this.y,e,t),this.z=Ve(this.z,e,t),this.w=Ve(this.w,e,t),this}clampLength(e,t){const i=this.length();return this.divideScalar(i||1).multiplyScalar(Ve(i,e,t))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,i){return this.x=e.x+(t.x-e.x)*i,this.y=e.y+(t.y-e.y)*i,this.z=e.z+(t.z-e.z)*i,this.w=e.w+(t.w-e.w)*i,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class Hy extends Er{constructor(e=1,t=1,i={}){super(),i=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:qn,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1,depth:1,multiview:!1},i),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=i.depth,this.scissor=new yt(0,0,e,t),this.scissorTest=!1,this.viewport=new yt(0,0,e,t);const r={width:e,height:t,depth:i.depth},s=new Yt(r);this.textures=[];const o=i.count;for(let a=0;a<o;a++)this.textures[a]=s.clone(),this.textures[a].isRenderTargetTexture=!0,this.textures[a].renderTarget=this;this._setTextureOptions(i),this.depthBuffer=i.depthBuffer,this.stencilBuffer=i.stencilBuffer,this.resolveDepthBuffer=i.resolveDepthBuffer,this.resolveStencilBuffer=i.resolveStencilBuffer,this._depthTexture=null,this.depthTexture=i.depthTexture,this.samples=i.samples,this.multiview=i.multiview}_setTextureOptions(e={}){const t={minFilter:qn,generateMipmaps:!1,flipY:!1,internalFormat:null};e.mapping!==void 0&&(t.mapping=e.mapping),e.wrapS!==void 0&&(t.wrapS=e.wrapS),e.wrapT!==void 0&&(t.wrapT=e.wrapT),e.wrapR!==void 0&&(t.wrapR=e.wrapR),e.magFilter!==void 0&&(t.magFilter=e.magFilter),e.minFilter!==void 0&&(t.minFilter=e.minFilter),e.format!==void 0&&(t.format=e.format),e.type!==void 0&&(t.type=e.type),e.anisotropy!==void 0&&(t.anisotropy=e.anisotropy),e.colorSpace!==void 0&&(t.colorSpace=e.colorSpace),e.flipY!==void 0&&(t.flipY=e.flipY),e.generateMipmaps!==void 0&&(t.generateMipmaps=e.generateMipmaps),e.internalFormat!==void 0&&(t.internalFormat=e.internalFormat);for(let i=0;i<this.textures.length;i++)this.textures[i].setValues(t)}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}set depthTexture(e){this._depthTexture!==null&&(this._depthTexture.renderTarget=null),e!==null&&(e.renderTarget=this),this._depthTexture=e}get depthTexture(){return this._depthTexture}setSize(e,t,i=1){if(this.width!==e||this.height!==t||this.depth!==i){this.width=e,this.height=t,this.depth=i;for(let r=0,s=this.textures.length;r<s;r++)this.textures[r].image.width=e,this.textures[r].image.height=t,this.textures[r].image.depth=i,this.textures[r].isArrayTexture=this.textures[r].image.depth>1;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let t=0,i=e.textures.length;t<i;t++){this.textures[t]=e.textures[t].clone(),this.textures[t].isRenderTargetTexture=!0,this.textures[t].renderTarget=this;const r=Object.assign({},e.textures[t].image);this.textures[t].source=new ju(r)}return this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class xr extends Hy{constructor(e=1,t=1,i={}){super(e,t,i),this.isWebGLRenderTarget=!0}}class Jp extends Yt{constructor(e=null,t=1,i=1,r=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:i,depth:r},this.magFilter=kn,this.minFilter=kn,this.wrapR=lr,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class Gy extends Yt{constructor(e=null,t=1,i=1,r=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:i,depth:r},this.magFilter=kn,this.minFilter=kn,this.wrapR=lr,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class _o{constructor(e=new B(1/0,1/0,1/0),t=new B(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,i=e.length;t<i;t+=3)this.expandByPoint(In.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,i=e.count;t<i;t++)this.expandByPoint(In.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,i=e.length;t<i;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const i=In.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(i),this.max.copy(e).add(i),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const i=e.geometry;if(i!==void 0){const s=i.getAttribute("position");if(t===!0&&s!==void 0&&e.isInstancedMesh!==!0)for(let o=0,a=s.count;o<a;o++)e.isMesh===!0?e.getVertexPosition(o,In):In.fromBufferAttribute(s,o),In.applyMatrix4(e.matrixWorld),this.expandByPoint(In);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),To.copy(e.boundingBox)):(i.boundingBox===null&&i.computeBoundingBox(),To.copy(i.boundingBox)),To.applyMatrix4(e.matrixWorld),this.union(To)}const r=e.children;for(let s=0,o=r.length;s<o;s++)this.expandByObject(r[s],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,In),In.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,i;return e.normal.x>0?(t=e.normal.x*this.min.x,i=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,i=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,i+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,i+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,i+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,i+=e.normal.z*this.min.z),t<=-e.constant&&i>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(As),Ao.subVectors(this.max,As),Pr.subVectors(e.a,As),Rr.subVectors(e.b,As),Dr.subVectors(e.c,As),bi.subVectors(Rr,Pr),Si.subVectors(Dr,Rr),ji.subVectors(Pr,Dr);let t=[0,-bi.z,bi.y,0,-Si.z,Si.y,0,-ji.z,ji.y,bi.z,0,-bi.x,Si.z,0,-Si.x,ji.z,0,-ji.x,-bi.y,bi.x,0,-Si.y,Si.x,0,-ji.y,ji.x,0];return!gl(t,Pr,Rr,Dr,Ao)||(t=[1,0,0,0,1,0,0,0,1],!gl(t,Pr,Rr,Dr,Ao))?!1:(Co.crossVectors(bi,Si),t=[Co.x,Co.y,Co.z],gl(t,Pr,Rr,Dr,Ao))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,In).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(In).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(ri[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),ri[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),ri[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),ri[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),ri[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),ri[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),ri[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),ri[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(ri),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}toJSON(){return{min:this.min.toArray(),max:this.max.toArray()}}fromJSON(e){return this.min.fromArray(e.min),this.max.fromArray(e.max),this}}const ri=[new B,new B,new B,new B,new B,new B,new B,new B],In=new B,To=new _o,Pr=new B,Rr=new B,Dr=new B,bi=new B,Si=new B,ji=new B,As=new B,Ao=new B,Co=new B,Ki=new B;function gl(n,e,t,i,r){for(let s=0,o=n.length-3;s<=o;s+=3){Ki.fromArray(n,s);const a=r.x*Math.abs(Ki.x)+r.y*Math.abs(Ki.y)+r.z*Math.abs(Ki.z),l=e.dot(Ki),c=t.dot(Ki),u=i.dot(Ki);if(Math.max(-Math.max(l,c,u),Math.min(l,c,u))>a)return!1}return!0}const Wy=new _o,Cs=new B,_l=new B;class za{constructor(e=new B,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const i=this.center;t!==void 0?i.copy(t):Wy.setFromPoints(e).getCenter(i);let r=0;for(let s=0,o=e.length;s<o;s++)r=Math.max(r,i.distanceToSquared(e[s]));return this.radius=Math.sqrt(r),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const i=this.center.distanceToSquared(e);return t.copy(e),i>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;Cs.subVectors(e,this.center);const t=Cs.lengthSq();if(t>this.radius*this.radius){const i=Math.sqrt(t),r=(i-this.radius)*.5;this.center.addScaledVector(Cs,r/i),this.radius+=r}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(_l.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(Cs.copy(e.center).add(_l)),this.expandByPoint(Cs.copy(e.center).sub(_l))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}toJSON(){return{radius:this.radius,center:this.center.toArray()}}fromJSON(e){return this.radius=e.radius,this.center.fromArray(e.center),this}}const si=new B,vl=new B,Po=new B,Ei=new B,xl=new B,Ro=new B,wl=new B;class Ku{constructor(e=new B,t=new B(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,si)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const i=t.dot(this.direction);return i<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,i)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=si.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(si.copy(this.origin).addScaledVector(this.direction,t),si.distanceToSquared(e))}distanceSqToSegment(e,t,i,r){vl.copy(e).add(t).multiplyScalar(.5),Po.copy(t).sub(e).normalize(),Ei.copy(this.origin).sub(vl);const s=e.distanceTo(t)*.5,o=-this.direction.dot(Po),a=Ei.dot(this.direction),l=-Ei.dot(Po),c=Ei.lengthSq(),u=Math.abs(1-o*o);let d,p,f,_;if(u>0)if(d=o*l-a,p=o*a-l,_=s*u,d>=0)if(p>=-_)if(p<=_){const g=1/u;d*=g,p*=g,f=d*(d+o*p+2*a)+p*(o*d+p+2*l)+c}else p=s,d=Math.max(0,-(o*p+a)),f=-d*d+p*(p+2*l)+c;else p=-s,d=Math.max(0,-(o*p+a)),f=-d*d+p*(p+2*l)+c;else p<=-_?(d=Math.max(0,-(-o*s+a)),p=d>0?-s:Math.min(Math.max(-s,-l),s),f=-d*d+p*(p+2*l)+c):p<=_?(d=0,p=Math.min(Math.max(-s,-l),s),f=p*(p+2*l)+c):(d=Math.max(0,-(o*s+a)),p=d>0?s:Math.min(Math.max(-s,-l),s),f=-d*d+p*(p+2*l)+c);else p=o>0?-s:s,d=Math.max(0,-(o*p+a)),f=-d*d+p*(p+2*l)+c;return i&&i.copy(this.origin).addScaledVector(this.direction,d),r&&r.copy(vl).addScaledVector(Po,p),f}intersectSphere(e,t){si.subVectors(e.center,this.origin);const i=si.dot(this.direction),r=si.dot(si)-i*i,s=e.radius*e.radius;if(r>s)return null;const o=Math.sqrt(s-r),a=i-o,l=i+o;return l<0?null:a<0?this.at(l,t):this.at(a,t)}intersectsSphere(e){return e.radius<0?!1:this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const i=-(this.origin.dot(e.normal)+e.constant)/t;return i>=0?i:null}intersectPlane(e,t){const i=this.distanceToPlane(e);return i===null?null:this.at(i,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let i,r,s,o,a,l;const c=1/this.direction.x,u=1/this.direction.y,d=1/this.direction.z,p=this.origin;return c>=0?(i=(e.min.x-p.x)*c,r=(e.max.x-p.x)*c):(i=(e.max.x-p.x)*c,r=(e.min.x-p.x)*c),u>=0?(s=(e.min.y-p.y)*u,o=(e.max.y-p.y)*u):(s=(e.max.y-p.y)*u,o=(e.min.y-p.y)*u),i>o||s>r||((s>i||isNaN(i))&&(i=s),(o<r||isNaN(r))&&(r=o),d>=0?(a=(e.min.z-p.z)*d,l=(e.max.z-p.z)*d):(a=(e.max.z-p.z)*d,l=(e.min.z-p.z)*d),i>l||a>r)||((a>i||i!==i)&&(i=a),(l<r||r!==r)&&(r=l),r<0)?null:this.at(i>=0?i:r,t)}intersectsBox(e){return this.intersectBox(e,si)!==null}intersectTriangle(e,t,i,r,s){xl.subVectors(t,e),Ro.subVectors(i,e),wl.crossVectors(xl,Ro);let o=this.direction.dot(wl),a;if(o>0){if(r)return null;a=1}else if(o<0)a=-1,o=-o;else return null;Ei.subVectors(this.origin,e);const l=a*this.direction.dot(Ro.crossVectors(Ei,Ro));if(l<0)return null;const c=a*this.direction.dot(xl.cross(Ei));if(c<0||l+c>o)return null;const u=-a*Ei.dot(wl);return u<0?null:this.at(u/o,s)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class Tt{constructor(e,t,i,r,s,o,a,l,c,u,d,p,f,_,g,m){Tt.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,i,r,s,o,a,l,c,u,d,p,f,_,g,m)}set(e,t,i,r,s,o,a,l,c,u,d,p,f,_,g,m){const h=this.elements;return h[0]=e,h[4]=t,h[8]=i,h[12]=r,h[1]=s,h[5]=o,h[9]=a,h[13]=l,h[2]=c,h[6]=u,h[10]=d,h[14]=p,h[3]=f,h[7]=_,h[11]=g,h[15]=m,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new Tt().fromArray(this.elements)}copy(e){const t=this.elements,i=e.elements;return t[0]=i[0],t[1]=i[1],t[2]=i[2],t[3]=i[3],t[4]=i[4],t[5]=i[5],t[6]=i[6],t[7]=i[7],t[8]=i[8],t[9]=i[9],t[10]=i[10],t[11]=i[11],t[12]=i[12],t[13]=i[13],t[14]=i[14],t[15]=i[15],this}copyPosition(e){const t=this.elements,i=e.elements;return t[12]=i[12],t[13]=i[13],t[14]=i[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,i){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),i.setFromMatrixColumn(this,2),this}makeBasis(e,t,i){return this.set(e.x,t.x,i.x,0,e.y,t.y,i.y,0,e.z,t.z,i.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,i=e.elements,r=1/Lr.setFromMatrixColumn(e,0).length(),s=1/Lr.setFromMatrixColumn(e,1).length(),o=1/Lr.setFromMatrixColumn(e,2).length();return t[0]=i[0]*r,t[1]=i[1]*r,t[2]=i[2]*r,t[3]=0,t[4]=i[4]*s,t[5]=i[5]*s,t[6]=i[6]*s,t[7]=0,t[8]=i[8]*o,t[9]=i[9]*o,t[10]=i[10]*o,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,i=e.x,r=e.y,s=e.z,o=Math.cos(i),a=Math.sin(i),l=Math.cos(r),c=Math.sin(r),u=Math.cos(s),d=Math.sin(s);if(e.order==="XYZ"){const p=o*u,f=o*d,_=a*u,g=a*d;t[0]=l*u,t[4]=-l*d,t[8]=c,t[1]=f+_*c,t[5]=p-g*c,t[9]=-a*l,t[2]=g-p*c,t[6]=_+f*c,t[10]=o*l}else if(e.order==="YXZ"){const p=l*u,f=l*d,_=c*u,g=c*d;t[0]=p+g*a,t[4]=_*a-f,t[8]=o*c,t[1]=o*d,t[5]=o*u,t[9]=-a,t[2]=f*a-_,t[6]=g+p*a,t[10]=o*l}else if(e.order==="ZXY"){const p=l*u,f=l*d,_=c*u,g=c*d;t[0]=p-g*a,t[4]=-o*d,t[8]=_+f*a,t[1]=f+_*a,t[5]=o*u,t[9]=g-p*a,t[2]=-o*c,t[6]=a,t[10]=o*l}else if(e.order==="ZYX"){const p=o*u,f=o*d,_=a*u,g=a*d;t[0]=l*u,t[4]=_*c-f,t[8]=p*c+g,t[1]=l*d,t[5]=g*c+p,t[9]=f*c-_,t[2]=-c,t[6]=a*l,t[10]=o*l}else if(e.order==="YZX"){const p=o*l,f=o*c,_=a*l,g=a*c;t[0]=l*u,t[4]=g-p*d,t[8]=_*d+f,t[1]=d,t[5]=o*u,t[9]=-a*u,t[2]=-c*u,t[6]=f*d+_,t[10]=p-g*d}else if(e.order==="XZY"){const p=o*l,f=o*c,_=a*l,g=a*c;t[0]=l*u,t[4]=-d,t[8]=c*u,t[1]=p*d+g,t[5]=o*u,t[9]=f*d-_,t[2]=_*d-f,t[6]=a*u,t[10]=g*d+p}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(Xy,e,$y)}lookAt(e,t,i){const r=this.elements;return un.subVectors(e,t),un.lengthSq()===0&&(un.z=1),un.normalize(),Mi.crossVectors(i,un),Mi.lengthSq()===0&&(Math.abs(i.z)===1?un.x+=1e-4:un.z+=1e-4,un.normalize(),Mi.crossVectors(i,un)),Mi.normalize(),Do.crossVectors(un,Mi),r[0]=Mi.x,r[4]=Do.x,r[8]=un.x,r[1]=Mi.y,r[5]=Do.y,r[9]=un.y,r[2]=Mi.z,r[6]=Do.z,r[10]=un.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const i=e.elements,r=t.elements,s=this.elements,o=i[0],a=i[4],l=i[8],c=i[12],u=i[1],d=i[5],p=i[9],f=i[13],_=i[2],g=i[6],m=i[10],h=i[14],v=i[3],x=i[7],w=i[11],S=i[15],C=r[0],T=r[4],A=r[8],b=r[12],y=r[1],P=r[5],D=r[9],O=r[13],V=r[2],k=r[6],G=r[10],$=r[14],U=r[3],Z=r[7],ee=r[11],ce=r[15];return s[0]=o*C+a*y+l*V+c*U,s[4]=o*T+a*P+l*k+c*Z,s[8]=o*A+a*D+l*G+c*ee,s[12]=o*b+a*O+l*$+c*ce,s[1]=u*C+d*y+p*V+f*U,s[5]=u*T+d*P+p*k+f*Z,s[9]=u*A+d*D+p*G+f*ee,s[13]=u*b+d*O+p*$+f*ce,s[2]=_*C+g*y+m*V+h*U,s[6]=_*T+g*P+m*k+h*Z,s[10]=_*A+g*D+m*G+h*ee,s[14]=_*b+g*O+m*$+h*ce,s[3]=v*C+x*y+w*V+S*U,s[7]=v*T+x*P+w*k+S*Z,s[11]=v*A+x*D+w*G+S*ee,s[15]=v*b+x*O+w*$+S*ce,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],i=e[4],r=e[8],s=e[12],o=e[1],a=e[5],l=e[9],c=e[13],u=e[2],d=e[6],p=e[10],f=e[14],_=e[3],g=e[7],m=e[11],h=e[15];return _*(+s*l*d-r*c*d-s*a*p+i*c*p+r*a*f-i*l*f)+g*(+t*l*f-t*c*p+s*o*p-r*o*f+r*c*u-s*l*u)+m*(+t*c*d-t*a*f-s*o*d+i*o*f+s*a*u-i*c*u)+h*(-r*a*u-t*l*d+t*a*p+r*o*d-i*o*p+i*l*u)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,i){const r=this.elements;return e.isVector3?(r[12]=e.x,r[13]=e.y,r[14]=e.z):(r[12]=e,r[13]=t,r[14]=i),this}invert(){const e=this.elements,t=e[0],i=e[1],r=e[2],s=e[3],o=e[4],a=e[5],l=e[6],c=e[7],u=e[8],d=e[9],p=e[10],f=e[11],_=e[12],g=e[13],m=e[14],h=e[15],v=d*m*c-g*p*c+g*l*f-a*m*f-d*l*h+a*p*h,x=_*p*c-u*m*c-_*l*f+o*m*f+u*l*h-o*p*h,w=u*g*c-_*d*c+_*a*f-o*g*f-u*a*h+o*d*h,S=_*d*l-u*g*l-_*a*p+o*g*p+u*a*m-o*d*m,C=t*v+i*x+r*w+s*S;if(C===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const T=1/C;return e[0]=v*T,e[1]=(g*p*s-d*m*s-g*r*f+i*m*f+d*r*h-i*p*h)*T,e[2]=(a*m*s-g*l*s+g*r*c-i*m*c-a*r*h+i*l*h)*T,e[3]=(d*l*s-a*p*s-d*r*c+i*p*c+a*r*f-i*l*f)*T,e[4]=x*T,e[5]=(u*m*s-_*p*s+_*r*f-t*m*f-u*r*h+t*p*h)*T,e[6]=(_*l*s-o*m*s-_*r*c+t*m*c+o*r*h-t*l*h)*T,e[7]=(o*p*s-u*l*s+u*r*c-t*p*c-o*r*f+t*l*f)*T,e[8]=w*T,e[9]=(_*d*s-u*g*s-_*i*f+t*g*f+u*i*h-t*d*h)*T,e[10]=(o*g*s-_*a*s+_*i*c-t*g*c-o*i*h+t*a*h)*T,e[11]=(u*a*s-o*d*s-u*i*c+t*d*c+o*i*f-t*a*f)*T,e[12]=S*T,e[13]=(u*g*r-_*d*r+_*i*p-t*g*p-u*i*m+t*d*m)*T,e[14]=(_*a*r-o*g*r-_*i*l+t*g*l+o*i*m-t*a*m)*T,e[15]=(o*d*r-u*a*r+u*i*l-t*d*l-o*i*p+t*a*p)*T,this}scale(e){const t=this.elements,i=e.x,r=e.y,s=e.z;return t[0]*=i,t[4]*=r,t[8]*=s,t[1]*=i,t[5]*=r,t[9]*=s,t[2]*=i,t[6]*=r,t[10]*=s,t[3]*=i,t[7]*=r,t[11]*=s,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],i=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],r=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,i,r))}makeTranslation(e,t,i){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,i,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),i=Math.sin(e);return this.set(1,0,0,0,0,t,-i,0,0,i,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),i=Math.sin(e);return this.set(t,0,i,0,0,1,0,0,-i,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),i=Math.sin(e);return this.set(t,-i,0,0,i,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const i=Math.cos(t),r=Math.sin(t),s=1-i,o=e.x,a=e.y,l=e.z,c=s*o,u=s*a;return this.set(c*o+i,c*a-r*l,c*l+r*a,0,c*a+r*l,u*a+i,u*l-r*o,0,c*l-r*a,u*l+r*o,s*l*l+i,0,0,0,0,1),this}makeScale(e,t,i){return this.set(e,0,0,0,0,t,0,0,0,0,i,0,0,0,0,1),this}makeShear(e,t,i,r,s,o){return this.set(1,i,s,0,e,1,o,0,t,r,1,0,0,0,0,1),this}compose(e,t,i){const r=this.elements,s=t._x,o=t._y,a=t._z,l=t._w,c=s+s,u=o+o,d=a+a,p=s*c,f=s*u,_=s*d,g=o*u,m=o*d,h=a*d,v=l*c,x=l*u,w=l*d,S=i.x,C=i.y,T=i.z;return r[0]=(1-(g+h))*S,r[1]=(f+w)*S,r[2]=(_-x)*S,r[3]=0,r[4]=(f-w)*C,r[5]=(1-(p+h))*C,r[6]=(m+v)*C,r[7]=0,r[8]=(_+x)*T,r[9]=(m-v)*T,r[10]=(1-(p+g))*T,r[11]=0,r[12]=e.x,r[13]=e.y,r[14]=e.z,r[15]=1,this}decompose(e,t,i){const r=this.elements;let s=Lr.set(r[0],r[1],r[2]).length();const o=Lr.set(r[4],r[5],r[6]).length(),a=Lr.set(r[8],r[9],r[10]).length();this.determinant()<0&&(s=-s),e.x=r[12],e.y=r[13],e.z=r[14],Un.copy(this);const c=1/s,u=1/o,d=1/a;return Un.elements[0]*=c,Un.elements[1]*=c,Un.elements[2]*=c,Un.elements[4]*=u,Un.elements[5]*=u,Un.elements[6]*=u,Un.elements[8]*=d,Un.elements[9]*=d,Un.elements[10]*=d,t.setFromRotationMatrix(Un),i.x=s,i.y=o,i.z=a,this}makePerspective(e,t,i,r,s,o,a=Yn,l=!1){const c=this.elements,u=2*s/(t-e),d=2*s/(i-r),p=(t+e)/(t-e),f=(i+r)/(i-r);let _,g;if(l)_=s/(o-s),g=o*s/(o-s);else if(a===Yn)_=-(o+s)/(o-s),g=-2*o*s/(o-s);else if(a===Sa)_=-o/(o-s),g=-o*s/(o-s);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+a);return c[0]=u,c[4]=0,c[8]=p,c[12]=0,c[1]=0,c[5]=d,c[9]=f,c[13]=0,c[2]=0,c[6]=0,c[10]=_,c[14]=g,c[3]=0,c[7]=0,c[11]=-1,c[15]=0,this}makeOrthographic(e,t,i,r,s,o,a=Yn,l=!1){const c=this.elements,u=2/(t-e),d=2/(i-r),p=-(t+e)/(t-e),f=-(i+r)/(i-r);let _,g;if(l)_=1/(o-s),g=o/(o-s);else if(a===Yn)_=-2/(o-s),g=-(o+s)/(o-s);else if(a===Sa)_=-1/(o-s),g=-s/(o-s);else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+a);return c[0]=u,c[4]=0,c[8]=0,c[12]=p,c[1]=0,c[5]=d,c[9]=0,c[13]=f,c[2]=0,c[6]=0,c[10]=_,c[14]=g,c[3]=0,c[7]=0,c[11]=0,c[15]=1,this}equals(e){const t=this.elements,i=e.elements;for(let r=0;r<16;r++)if(t[r]!==i[r])return!1;return!0}fromArray(e,t=0){for(let i=0;i<16;i++)this.elements[i]=e[i+t];return this}toArray(e=[],t=0){const i=this.elements;return e[t]=i[0],e[t+1]=i[1],e[t+2]=i[2],e[t+3]=i[3],e[t+4]=i[4],e[t+5]=i[5],e[t+6]=i[6],e[t+7]=i[7],e[t+8]=i[8],e[t+9]=i[9],e[t+10]=i[10],e[t+11]=i[11],e[t+12]=i[12],e[t+13]=i[13],e[t+14]=i[14],e[t+15]=i[15],e}}const Lr=new B,Un=new Tt,Xy=new B(0,0,0),$y=new B(1,1,1),Mi=new B,Do=new B,un=new B,lh=new Tt,ch=new vr;class vi{constructor(e=0,t=0,i=0,r=vi.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=i,this._order=r}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,i,r=this._order){return this._x=e,this._y=t,this._z=i,this._order=r,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,i=!0){const r=e.elements,s=r[0],o=r[4],a=r[8],l=r[1],c=r[5],u=r[9],d=r[2],p=r[6],f=r[10];switch(t){case"XYZ":this._y=Math.asin(Ve(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(-u,f),this._z=Math.atan2(-o,s)):(this._x=Math.atan2(p,c),this._z=0);break;case"YXZ":this._x=Math.asin(-Ve(u,-1,1)),Math.abs(u)<.9999999?(this._y=Math.atan2(a,f),this._z=Math.atan2(l,c)):(this._y=Math.atan2(-d,s),this._z=0);break;case"ZXY":this._x=Math.asin(Ve(p,-1,1)),Math.abs(p)<.9999999?(this._y=Math.atan2(-d,f),this._z=Math.atan2(-o,c)):(this._y=0,this._z=Math.atan2(l,s));break;case"ZYX":this._y=Math.asin(-Ve(d,-1,1)),Math.abs(d)<.9999999?(this._x=Math.atan2(p,f),this._z=Math.atan2(l,s)):(this._x=0,this._z=Math.atan2(-o,c));break;case"YZX":this._z=Math.asin(Ve(l,-1,1)),Math.abs(l)<.9999999?(this._x=Math.atan2(-u,c),this._y=Math.atan2(-d,s)):(this._x=0,this._y=Math.atan2(a,f));break;case"XZY":this._z=Math.asin(-Ve(o,-1,1)),Math.abs(o)<.9999999?(this._x=Math.atan2(p,c),this._y=Math.atan2(a,s)):(this._x=Math.atan2(-u,f),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,i===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,i){return lh.makeRotationFromQuaternion(e),this.setFromRotationMatrix(lh,t,i)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return ch.setFromEuler(this),this.setFromQuaternion(ch,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}vi.DEFAULT_ORDER="XYZ";class Qp{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let qy=0;const uh=new B,Ir=new vr,oi=new Tt,Lo=new B,Ps=new B,Yy=new B,jy=new vr,dh=new B(1,0,0),hh=new B(0,1,0),fh=new B(0,0,1),ph={type:"added"},Ky={type:"removed"},Ur={type:"childadded",child:null},yl={type:"childremoved",child:null};class tn extends Er{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:qy++}),this.uuid=bs(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=tn.DEFAULT_UP.clone();const e=new B,t=new vi,i=new vr,r=new B(1,1,1);function s(){i.setFromEuler(t,!1)}function o(){t.setFromQuaternion(i,void 0,!1)}t._onChange(s),i._onChange(o),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:i},scale:{configurable:!0,enumerable:!0,value:r},modelViewMatrix:{value:new Tt},normalMatrix:{value:new Fe}}),this.matrix=new Tt,this.matrixWorld=new Tt,this.matrixAutoUpdate=tn.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=tn.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new Qp,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.customDepthMaterial=void 0,this.customDistanceMaterial=void 0,this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return Ir.setFromAxisAngle(e,t),this.quaternion.multiply(Ir),this}rotateOnWorldAxis(e,t){return Ir.setFromAxisAngle(e,t),this.quaternion.premultiply(Ir),this}rotateX(e){return this.rotateOnAxis(dh,e)}rotateY(e){return this.rotateOnAxis(hh,e)}rotateZ(e){return this.rotateOnAxis(fh,e)}translateOnAxis(e,t){return uh.copy(e).applyQuaternion(this.quaternion),this.position.add(uh.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(dh,e)}translateY(e){return this.translateOnAxis(hh,e)}translateZ(e){return this.translateOnAxis(fh,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(oi.copy(this.matrixWorld).invert())}lookAt(e,t,i){e.isVector3?Lo.copy(e):Lo.set(e,t,i);const r=this.parent;this.updateWorldMatrix(!0,!1),Ps.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?oi.lookAt(Ps,Lo,this.up):oi.lookAt(Lo,Ps,this.up),this.quaternion.setFromRotationMatrix(oi),r&&(oi.extractRotation(r.matrixWorld),Ir.setFromRotationMatrix(oi),this.quaternion.premultiply(Ir.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(ph),Ur.child=e,this.dispatchEvent(Ur),Ur.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let i=0;i<arguments.length;i++)this.remove(arguments[i]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(Ky),yl.child=e,this.dispatchEvent(yl),yl.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),oi.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),oi.multiply(e.parent.matrixWorld)),e.applyMatrix4(oi),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(ph),Ur.child=e,this.dispatchEvent(Ur),Ur.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let i=0,r=this.children.length;i<r;i++){const o=this.children[i].getObjectByProperty(e,t);if(o!==void 0)return o}}getObjectsByProperty(e,t,i=[]){this[e]===t&&i.push(this);const r=this.children;for(let s=0,o=r.length;s<o;s++)r[s].getObjectsByProperty(e,t,i);return i}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Ps,e,Yy),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Ps,jy,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let i=0,r=t.length;i<r;i++)t[i].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let i=0,r=t.length;i<r;i++)t[i].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let i=0,r=t.length;i<r;i++)t[i].updateMatrixWorld(e)}updateWorldMatrix(e,t){const i=this.parent;if(e===!0&&i!==null&&i.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const r=this.children;for(let s=0,o=r.length;s<o;s++)r[s].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",i={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},i.metadata={version:4.7,type:"Object",generator:"Object3D.toJSON"});const r={};r.uuid=this.uuid,r.type=this.type,this.name!==""&&(r.name=this.name),this.castShadow===!0&&(r.castShadow=!0),this.receiveShadow===!0&&(r.receiveShadow=!0),this.visible===!1&&(r.visible=!1),this.frustumCulled===!1&&(r.frustumCulled=!1),this.renderOrder!==0&&(r.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(r.userData=this.userData),r.layers=this.layers.mask,r.matrix=this.matrix.toArray(),r.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(r.matrixAutoUpdate=!1),this.isInstancedMesh&&(r.type="InstancedMesh",r.count=this.count,r.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(r.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(r.type="BatchedMesh",r.perObjectFrustumCulled=this.perObjectFrustumCulled,r.sortObjects=this.sortObjects,r.drawRanges=this._drawRanges,r.reservedRanges=this._reservedRanges,r.geometryInfo=this._geometryInfo.map(a=>({...a,boundingBox:a.boundingBox?a.boundingBox.toJSON():void 0,boundingSphere:a.boundingSphere?a.boundingSphere.toJSON():void 0})),r.instanceInfo=this._instanceInfo.map(a=>({...a})),r.availableInstanceIds=this._availableInstanceIds.slice(),r.availableGeometryIds=this._availableGeometryIds.slice(),r.nextIndexStart=this._nextIndexStart,r.nextVertexStart=this._nextVertexStart,r.geometryCount=this._geometryCount,r.maxInstanceCount=this._maxInstanceCount,r.maxVertexCount=this._maxVertexCount,r.maxIndexCount=this._maxIndexCount,r.geometryInitialized=this._geometryInitialized,r.matricesTexture=this._matricesTexture.toJSON(e),r.indirectTexture=this._indirectTexture.toJSON(e),this._colorsTexture!==null&&(r.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(r.boundingSphere=this.boundingSphere.toJSON()),this.boundingBox!==null&&(r.boundingBox=this.boundingBox.toJSON()));function s(a,l){return a[l.uuid]===void 0&&(a[l.uuid]=l.toJSON(e)),l.uuid}if(this.isScene)this.background&&(this.background.isColor?r.background=this.background.toJSON():this.background.isTexture&&(r.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(r.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){r.geometry=s(e.geometries,this.geometry);const a=this.geometry.parameters;if(a!==void 0&&a.shapes!==void 0){const l=a.shapes;if(Array.isArray(l))for(let c=0,u=l.length;c<u;c++){const d=l[c];s(e.shapes,d)}else s(e.shapes,l)}}if(this.isSkinnedMesh&&(r.bindMode=this.bindMode,r.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(s(e.skeletons,this.skeleton),r.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const a=[];for(let l=0,c=this.material.length;l<c;l++)a.push(s(e.materials,this.material[l]));r.material=a}else r.material=s(e.materials,this.material);if(this.children.length>0){r.children=[];for(let a=0;a<this.children.length;a++)r.children.push(this.children[a].toJSON(e).object)}if(this.animations.length>0){r.animations=[];for(let a=0;a<this.animations.length;a++){const l=this.animations[a];r.animations.push(s(e.animations,l))}}if(t){const a=o(e.geometries),l=o(e.materials),c=o(e.textures),u=o(e.images),d=o(e.shapes),p=o(e.skeletons),f=o(e.animations),_=o(e.nodes);a.length>0&&(i.geometries=a),l.length>0&&(i.materials=l),c.length>0&&(i.textures=c),u.length>0&&(i.images=u),d.length>0&&(i.shapes=d),p.length>0&&(i.skeletons=p),f.length>0&&(i.animations=f),_.length>0&&(i.nodes=_)}return i.object=r,i;function o(a){const l=[];for(const c in a){const u=a[c];delete u.metadata,l.push(u)}return l}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let i=0;i<e.children.length;i++){const r=e.children[i];this.add(r.clone())}return this}}tn.DEFAULT_UP=new B(0,1,0);tn.DEFAULT_MATRIX_AUTO_UPDATE=!0;tn.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const On=new B,ai=new B,bl=new B,li=new B,Or=new B,Fr=new B,mh=new B,Sl=new B,El=new B,Ml=new B,Tl=new yt,Al=new yt,Cl=new yt;class Fn{constructor(e=new B,t=new B,i=new B){this.a=e,this.b=t,this.c=i}static getNormal(e,t,i,r){r.subVectors(i,t),On.subVectors(e,t),r.cross(On);const s=r.lengthSq();return s>0?r.multiplyScalar(1/Math.sqrt(s)):r.set(0,0,0)}static getBarycoord(e,t,i,r,s){On.subVectors(r,t),ai.subVectors(i,t),bl.subVectors(e,t);const o=On.dot(On),a=On.dot(ai),l=On.dot(bl),c=ai.dot(ai),u=ai.dot(bl),d=o*c-a*a;if(d===0)return s.set(0,0,0),null;const p=1/d,f=(c*l-a*u)*p,_=(o*u-a*l)*p;return s.set(1-f-_,_,f)}static containsPoint(e,t,i,r){return this.getBarycoord(e,t,i,r,li)===null?!1:li.x>=0&&li.y>=0&&li.x+li.y<=1}static getInterpolation(e,t,i,r,s,o,a,l){return this.getBarycoord(e,t,i,r,li)===null?(l.x=0,l.y=0,"z"in l&&(l.z=0),"w"in l&&(l.w=0),null):(l.setScalar(0),l.addScaledVector(s,li.x),l.addScaledVector(o,li.y),l.addScaledVector(a,li.z),l)}static getInterpolatedAttribute(e,t,i,r,s,o){return Tl.setScalar(0),Al.setScalar(0),Cl.setScalar(0),Tl.fromBufferAttribute(e,t),Al.fromBufferAttribute(e,i),Cl.fromBufferAttribute(e,r),o.setScalar(0),o.addScaledVector(Tl,s.x),o.addScaledVector(Al,s.y),o.addScaledVector(Cl,s.z),o}static isFrontFacing(e,t,i,r){return On.subVectors(i,t),ai.subVectors(e,t),On.cross(ai).dot(r)<0}set(e,t,i){return this.a.copy(e),this.b.copy(t),this.c.copy(i),this}setFromPointsAndIndices(e,t,i,r){return this.a.copy(e[t]),this.b.copy(e[i]),this.c.copy(e[r]),this}setFromAttributeAndIndices(e,t,i,r){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,i),this.c.fromBufferAttribute(e,r),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return On.subVectors(this.c,this.b),ai.subVectors(this.a,this.b),On.cross(ai).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return Fn.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return Fn.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,i,r,s){return Fn.getInterpolation(e,this.a,this.b,this.c,t,i,r,s)}containsPoint(e){return Fn.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return Fn.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const i=this.a,r=this.b,s=this.c;let o,a;Or.subVectors(r,i),Fr.subVectors(s,i),Sl.subVectors(e,i);const l=Or.dot(Sl),c=Fr.dot(Sl);if(l<=0&&c<=0)return t.copy(i);El.subVectors(e,r);const u=Or.dot(El),d=Fr.dot(El);if(u>=0&&d<=u)return t.copy(r);const p=l*d-u*c;if(p<=0&&l>=0&&u<=0)return o=l/(l-u),t.copy(i).addScaledVector(Or,o);Ml.subVectors(e,s);const f=Or.dot(Ml),_=Fr.dot(Ml);if(_>=0&&f<=_)return t.copy(s);const g=f*c-l*_;if(g<=0&&c>=0&&_<=0)return a=c/(c-_),t.copy(i).addScaledVector(Fr,a);const m=u*_-f*d;if(m<=0&&d-u>=0&&f-_>=0)return mh.subVectors(s,r),a=(d-u)/(d-u+(f-_)),t.copy(r).addScaledVector(mh,a);const h=1/(m+g+p);return o=g*h,a=p*h,t.copy(i).addScaledVector(Or,o).addScaledVector(Fr,a)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const em={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},Ti={h:0,s:0,l:0},Io={h:0,s:0,l:0};function Pl(n,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?n+(e-n)*6*t:t<1/2?e:t<2/3?n+(e-n)*6*(2/3-t):n}class Ze{constructor(e,t,i){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,i)}set(e,t,i){if(t===void 0&&i===void 0){const r=e;r&&r.isColor?this.copy(r):typeof r=="number"?this.setHex(r):typeof r=="string"&&this.setStyle(r)}else this.setRGB(e,t,i);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=An){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,qe.colorSpaceToWorking(this,t),this}setRGB(e,t,i,r=qe.workingColorSpace){return this.r=e,this.g=t,this.b=i,qe.colorSpaceToWorking(this,r),this}setHSL(e,t,i,r=qe.workingColorSpace){if(e=Yu(e,1),t=Ve(t,0,1),i=Ve(i,0,1),t===0)this.r=this.g=this.b=i;else{const s=i<=.5?i*(1+t):i+t-i*t,o=2*i-s;this.r=Pl(o,s,e+1/3),this.g=Pl(o,s,e),this.b=Pl(o,s,e-1/3)}return qe.colorSpaceToWorking(this,r),this}setStyle(e,t=An){function i(s){s!==void 0&&parseFloat(s)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let r;if(r=/^(\w+)\(([^\)]*)\)/.exec(e)){let s;const o=r[1],a=r[2];switch(o){case"rgb":case"rgba":if(s=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return i(s[4]),this.setRGB(Math.min(255,parseInt(s[1],10))/255,Math.min(255,parseInt(s[2],10))/255,Math.min(255,parseInt(s[3],10))/255,t);if(s=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return i(s[4]),this.setRGB(Math.min(100,parseInt(s[1],10))/100,Math.min(100,parseInt(s[2],10))/100,Math.min(100,parseInt(s[3],10))/100,t);break;case"hsl":case"hsla":if(s=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return i(s[4]),this.setHSL(parseFloat(s[1])/360,parseFloat(s[2])/100,parseFloat(s[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(r=/^\#([A-Fa-f\d]+)$/.exec(e)){const s=r[1],o=s.length;if(o===3)return this.setRGB(parseInt(s.charAt(0),16)/15,parseInt(s.charAt(1),16)/15,parseInt(s.charAt(2),16)/15,t);if(o===6)return this.setHex(parseInt(s,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=An){const i=em[e.toLowerCase()];return i!==void 0?this.setHex(i,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=gi(e.r),this.g=gi(e.g),this.b=gi(e.b),this}copyLinearToSRGB(e){return this.r=Jr(e.r),this.g=Jr(e.g),this.b=Jr(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=An){return qe.workingToColorSpace(Bt.copy(this),e),Math.round(Ve(Bt.r*255,0,255))*65536+Math.round(Ve(Bt.g*255,0,255))*256+Math.round(Ve(Bt.b*255,0,255))}getHexString(e=An){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=qe.workingColorSpace){qe.workingToColorSpace(Bt.copy(this),t);const i=Bt.r,r=Bt.g,s=Bt.b,o=Math.max(i,r,s),a=Math.min(i,r,s);let l,c;const u=(a+o)/2;if(a===o)l=0,c=0;else{const d=o-a;switch(c=u<=.5?d/(o+a):d/(2-o-a),o){case i:l=(r-s)/d+(r<s?6:0);break;case r:l=(s-i)/d+2;break;case s:l=(i-r)/d+4;break}l/=6}return e.h=l,e.s=c,e.l=u,e}getRGB(e,t=qe.workingColorSpace){return qe.workingToColorSpace(Bt.copy(this),t),e.r=Bt.r,e.g=Bt.g,e.b=Bt.b,e}getStyle(e=An){qe.workingToColorSpace(Bt.copy(this),e);const t=Bt.r,i=Bt.g,r=Bt.b;return e!==An?`color(${e} ${t.toFixed(3)} ${i.toFixed(3)} ${r.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(i*255)},${Math.round(r*255)})`}offsetHSL(e,t,i){return this.getHSL(Ti),this.setHSL(Ti.h+e,Ti.s+t,Ti.l+i)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,i){return this.r=e.r+(t.r-e.r)*i,this.g=e.g+(t.g-e.g)*i,this.b=e.b+(t.b-e.b)*i,this}lerpHSL(e,t){this.getHSL(Ti),e.getHSL(Io);const i=Bs(Ti.h,Io.h,t),r=Bs(Ti.s,Io.s,t),s=Bs(Ti.l,Io.l,t);return this.setHSL(i,r,s),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,i=this.g,r=this.b,s=e.elements;return this.r=s[0]*t+s[3]*i+s[6]*r,this.g=s[1]*t+s[4]*i+s[7]*r,this.b=s[2]*t+s[5]*i+s[8]*r,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const Bt=new Ze;Ze.NAMES=em;let Zy=0;class vo extends Er{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:Zy++}),this.uuid=bs(),this.name="",this.type="Material",this.blending=Zr,this.side=Hi,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=cc,this.blendDst=uc,this.blendEquation=sr,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new Ze(0,0,0),this.blendAlpha=0,this.depthFunc=ss,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=eh,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=Ar,this.stencilZFail=Ar,this.stencilZPass=Ar,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.allowOverride=!0,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const i=e[t];if(i===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const r=this[t];if(r===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}r&&r.isColor?r.set(i):r&&r.isVector3&&i&&i.isVector3?r.copy(i):this[t]=i}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const i={metadata:{version:4.7,type:"Material",generator:"Material.toJSON"}};i.uuid=this.uuid,i.type=this.type,this.name!==""&&(i.name=this.name),this.color&&this.color.isColor&&(i.color=this.color.getHex()),this.roughness!==void 0&&(i.roughness=this.roughness),this.metalness!==void 0&&(i.metalness=this.metalness),this.sheen!==void 0&&(i.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(i.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(i.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(i.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(i.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(i.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(i.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(i.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(i.shininess=this.shininess),this.clearcoat!==void 0&&(i.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(i.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(i.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(i.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(i.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,i.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.sheenColorMap&&this.sheenColorMap.isTexture&&(i.sheenColorMap=this.sheenColorMap.toJSON(e).uuid),this.sheenRoughnessMap&&this.sheenRoughnessMap.isTexture&&(i.sheenRoughnessMap=this.sheenRoughnessMap.toJSON(e).uuid),this.dispersion!==void 0&&(i.dispersion=this.dispersion),this.iridescence!==void 0&&(i.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(i.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(i.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(i.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(i.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(i.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(i.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(i.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(i.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(i.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(i.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(i.lightMap=this.lightMap.toJSON(e).uuid,i.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(i.aoMap=this.aoMap.toJSON(e).uuid,i.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(i.bumpMap=this.bumpMap.toJSON(e).uuid,i.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(i.normalMap=this.normalMap.toJSON(e).uuid,i.normalMapType=this.normalMapType,i.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(i.displacementMap=this.displacementMap.toJSON(e).uuid,i.displacementScale=this.displacementScale,i.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(i.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(i.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(i.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(i.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(i.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(i.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(i.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(i.combine=this.combine)),this.envMapRotation!==void 0&&(i.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(i.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(i.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(i.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(i.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(i.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(i.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(i.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(i.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(i.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(i.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(i.size=this.size),this.shadowSide!==null&&(i.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(i.sizeAttenuation=this.sizeAttenuation),this.blending!==Zr&&(i.blending=this.blending),this.side!==Hi&&(i.side=this.side),this.vertexColors===!0&&(i.vertexColors=!0),this.opacity<1&&(i.opacity=this.opacity),this.transparent===!0&&(i.transparent=!0),this.blendSrc!==cc&&(i.blendSrc=this.blendSrc),this.blendDst!==uc&&(i.blendDst=this.blendDst),this.blendEquation!==sr&&(i.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(i.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(i.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(i.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(i.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(i.blendAlpha=this.blendAlpha),this.depthFunc!==ss&&(i.depthFunc=this.depthFunc),this.depthTest===!1&&(i.depthTest=this.depthTest),this.depthWrite===!1&&(i.depthWrite=this.depthWrite),this.colorWrite===!1&&(i.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(i.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==eh&&(i.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(i.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(i.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==Ar&&(i.stencilFail=this.stencilFail),this.stencilZFail!==Ar&&(i.stencilZFail=this.stencilZFail),this.stencilZPass!==Ar&&(i.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(i.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(i.rotation=this.rotation),this.polygonOffset===!0&&(i.polygonOffset=!0),this.polygonOffsetFactor!==0&&(i.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(i.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(i.linewidth=this.linewidth),this.dashSize!==void 0&&(i.dashSize=this.dashSize),this.gapSize!==void 0&&(i.gapSize=this.gapSize),this.scale!==void 0&&(i.scale=this.scale),this.dithering===!0&&(i.dithering=!0),this.alphaTest>0&&(i.alphaTest=this.alphaTest),this.alphaHash===!0&&(i.alphaHash=!0),this.alphaToCoverage===!0&&(i.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(i.premultipliedAlpha=!0),this.forceSinglePass===!0&&(i.forceSinglePass=!0),this.wireframe===!0&&(i.wireframe=!0),this.wireframeLinewidth>1&&(i.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(i.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(i.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(i.flatShading=!0),this.visible===!1&&(i.visible=!1),this.toneMapped===!1&&(i.toneMapped=!1),this.fog===!1&&(i.fog=!1),Object.keys(this.userData).length>0&&(i.userData=this.userData);function r(s){const o=[];for(const a in s){const l=s[a];delete l.metadata,o.push(l)}return o}if(t){const s=r(e.textures),o=r(e.images);s.length>0&&(i.textures=s),o.length>0&&(i.images=o)}return i}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let i=null;if(t!==null){const r=t.length;i=new Array(r);for(let s=0;s!==r;++s)i[s]=t[s].clone()}return this.clippingPlanes=i,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}}class tm extends vo{constructor(e){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new Ze(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new vi,this.combine=zp,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const St=new B,Uo=new Be;let Jy=0;class Zn{constructor(e,t,i=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,Object.defineProperty(this,"id",{value:Jy++}),this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=i,this.usage=th,this.updateRanges=[],this.gpuType=fi,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,i){e*=this.itemSize,i*=t.itemSize;for(let r=0,s=this.itemSize;r<s;r++)this.array[e+r]=t.array[i+r];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,i=this.count;t<i;t++)Uo.fromBufferAttribute(this,t),Uo.applyMatrix3(e),this.setXY(t,Uo.x,Uo.y);else if(this.itemSize===3)for(let t=0,i=this.count;t<i;t++)St.fromBufferAttribute(this,t),St.applyMatrix3(e),this.setXYZ(t,St.x,St.y,St.z);return this}applyMatrix4(e){for(let t=0,i=this.count;t<i;t++)St.fromBufferAttribute(this,t),St.applyMatrix4(e),this.setXYZ(t,St.x,St.y,St.z);return this}applyNormalMatrix(e){for(let t=0,i=this.count;t<i;t++)St.fromBufferAttribute(this,t),St.applyNormalMatrix(e),this.setXYZ(t,St.x,St.y,St.z);return this}transformDirection(e){for(let t=0,i=this.count;t<i;t++)St.fromBufferAttribute(this,t),St.transformDirection(e),this.setXYZ(t,St.x,St.y,St.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let i=this.array[e*this.itemSize+t];return this.normalized&&(i=Gr(i,this.array)),i}setComponent(e,t,i){return this.normalized&&(i=Wt(i,this.array)),this.array[e*this.itemSize+t]=i,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=Gr(t,this.array)),t}setX(e,t){return this.normalized&&(t=Wt(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=Gr(t,this.array)),t}setY(e,t){return this.normalized&&(t=Wt(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=Gr(t,this.array)),t}setZ(e,t){return this.normalized&&(t=Wt(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=Gr(t,this.array)),t}setW(e,t){return this.normalized&&(t=Wt(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,i){return e*=this.itemSize,this.normalized&&(t=Wt(t,this.array),i=Wt(i,this.array)),this.array[e+0]=t,this.array[e+1]=i,this}setXYZ(e,t,i,r){return e*=this.itemSize,this.normalized&&(t=Wt(t,this.array),i=Wt(i,this.array),r=Wt(r,this.array)),this.array[e+0]=t,this.array[e+1]=i,this.array[e+2]=r,this}setXYZW(e,t,i,r,s){return e*=this.itemSize,this.normalized&&(t=Wt(t,this.array),i=Wt(i,this.array),r=Wt(r,this.array),s=Wt(s,this.array)),this.array[e+0]=t,this.array[e+1]=i,this.array[e+2]=r,this.array[e+3]=s,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==th&&(e.usage=this.usage),e}}class nm extends Zn{constructor(e,t,i){super(new Uint16Array(e),t,i)}}class im extends Zn{constructor(e,t,i){super(new Uint32Array(e),t,i)}}class Jn extends Zn{constructor(e,t,i){super(new Float32Array(e),t,i)}}let Qy=0;const En=new Tt,Rl=new tn,Nr=new B,dn=new _o,Rs=new _o,Lt=new B;class yi extends Er{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:Qy++}),this.uuid=bs(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(Zp(e)?im:nm)(e,1):this.index=e,this}setIndirect(e){return this.indirect=e,this}getIndirect(){return this.indirect}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,i=0){this.groups.push({start:e,count:t,materialIndex:i})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const i=this.attributes.normal;if(i!==void 0){const s=new Fe().getNormalMatrix(e);i.applyNormalMatrix(s),i.needsUpdate=!0}const r=this.attributes.tangent;return r!==void 0&&(r.transformDirection(e),r.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return En.makeRotationFromQuaternion(e),this.applyMatrix4(En),this}rotateX(e){return En.makeRotationX(e),this.applyMatrix4(En),this}rotateY(e){return En.makeRotationY(e),this.applyMatrix4(En),this}rotateZ(e){return En.makeRotationZ(e),this.applyMatrix4(En),this}translate(e,t,i){return En.makeTranslation(e,t,i),this.applyMatrix4(En),this}scale(e,t,i){return En.makeScale(e,t,i),this.applyMatrix4(En),this}lookAt(e){return Rl.lookAt(e),Rl.updateMatrix(),this.applyMatrix4(Rl.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(Nr).negate(),this.translate(Nr.x,Nr.y,Nr.z),this}setFromPoints(e){const t=this.getAttribute("position");if(t===void 0){const i=[];for(let r=0,s=e.length;r<s;r++){const o=e[r];i.push(o.x,o.y,o.z||0)}this.setAttribute("position",new Jn(i,3))}else{const i=Math.min(e.length,t.count);for(let r=0;r<i;r++){const s=e[r];t.setXYZ(r,s.x,s.y,s.z||0)}e.length>t.count&&console.warn("THREE.BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),t.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new _o);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new B(-1/0,-1/0,-1/0),new B(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let i=0,r=t.length;i<r;i++){const s=t[i];dn.setFromBufferAttribute(s),this.morphTargetsRelative?(Lt.addVectors(this.boundingBox.min,dn.min),this.boundingBox.expandByPoint(Lt),Lt.addVectors(this.boundingBox.max,dn.max),this.boundingBox.expandByPoint(Lt)):(this.boundingBox.expandByPoint(dn.min),this.boundingBox.expandByPoint(dn.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new za);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new B,1/0);return}if(e){const i=this.boundingSphere.center;if(dn.setFromBufferAttribute(e),t)for(let s=0,o=t.length;s<o;s++){const a=t[s];Rs.setFromBufferAttribute(a),this.morphTargetsRelative?(Lt.addVectors(dn.min,Rs.min),dn.expandByPoint(Lt),Lt.addVectors(dn.max,Rs.max),dn.expandByPoint(Lt)):(dn.expandByPoint(Rs.min),dn.expandByPoint(Rs.max))}dn.getCenter(i);let r=0;for(let s=0,o=e.count;s<o;s++)Lt.fromBufferAttribute(e,s),r=Math.max(r,i.distanceToSquared(Lt));if(t)for(let s=0,o=t.length;s<o;s++){const a=t[s],l=this.morphTargetsRelative;for(let c=0,u=a.count;c<u;c++)Lt.fromBufferAttribute(a,c),l&&(Nr.fromBufferAttribute(e,c),Lt.add(Nr)),r=Math.max(r,i.distanceToSquared(Lt))}this.boundingSphere.radius=Math.sqrt(r),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const i=t.position,r=t.normal,s=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new Zn(new Float32Array(4*i.count),4));const o=this.getAttribute("tangent"),a=[],l=[];for(let A=0;A<i.count;A++)a[A]=new B,l[A]=new B;const c=new B,u=new B,d=new B,p=new Be,f=new Be,_=new Be,g=new B,m=new B;function h(A,b,y){c.fromBufferAttribute(i,A),u.fromBufferAttribute(i,b),d.fromBufferAttribute(i,y),p.fromBufferAttribute(s,A),f.fromBufferAttribute(s,b),_.fromBufferAttribute(s,y),u.sub(c),d.sub(c),f.sub(p),_.sub(p);const P=1/(f.x*_.y-_.x*f.y);isFinite(P)&&(g.copy(u).multiplyScalar(_.y).addScaledVector(d,-f.y).multiplyScalar(P),m.copy(d).multiplyScalar(f.x).addScaledVector(u,-_.x).multiplyScalar(P),a[A].add(g),a[b].add(g),a[y].add(g),l[A].add(m),l[b].add(m),l[y].add(m))}let v=this.groups;v.length===0&&(v=[{start:0,count:e.count}]);for(let A=0,b=v.length;A<b;++A){const y=v[A],P=y.start,D=y.count;for(let O=P,V=P+D;O<V;O+=3)h(e.getX(O+0),e.getX(O+1),e.getX(O+2))}const x=new B,w=new B,S=new B,C=new B;function T(A){S.fromBufferAttribute(r,A),C.copy(S);const b=a[A];x.copy(b),x.sub(S.multiplyScalar(S.dot(b))).normalize(),w.crossVectors(C,b);const P=w.dot(l[A])<0?-1:1;o.setXYZW(A,x.x,x.y,x.z,P)}for(let A=0,b=v.length;A<b;++A){const y=v[A],P=y.start,D=y.count;for(let O=P,V=P+D;O<V;O+=3)T(e.getX(O+0)),T(e.getX(O+1)),T(e.getX(O+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let i=this.getAttribute("normal");if(i===void 0)i=new Zn(new Float32Array(t.count*3),3),this.setAttribute("normal",i);else for(let p=0,f=i.count;p<f;p++)i.setXYZ(p,0,0,0);const r=new B,s=new B,o=new B,a=new B,l=new B,c=new B,u=new B,d=new B;if(e)for(let p=0,f=e.count;p<f;p+=3){const _=e.getX(p+0),g=e.getX(p+1),m=e.getX(p+2);r.fromBufferAttribute(t,_),s.fromBufferAttribute(t,g),o.fromBufferAttribute(t,m),u.subVectors(o,s),d.subVectors(r,s),u.cross(d),a.fromBufferAttribute(i,_),l.fromBufferAttribute(i,g),c.fromBufferAttribute(i,m),a.add(u),l.add(u),c.add(u),i.setXYZ(_,a.x,a.y,a.z),i.setXYZ(g,l.x,l.y,l.z),i.setXYZ(m,c.x,c.y,c.z)}else for(let p=0,f=t.count;p<f;p+=3)r.fromBufferAttribute(t,p+0),s.fromBufferAttribute(t,p+1),o.fromBufferAttribute(t,p+2),u.subVectors(o,s),d.subVectors(r,s),u.cross(d),i.setXYZ(p+0,u.x,u.y,u.z),i.setXYZ(p+1,u.x,u.y,u.z),i.setXYZ(p+2,u.x,u.y,u.z);this.normalizeNormals(),i.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,i=e.count;t<i;t++)Lt.fromBufferAttribute(e,t),Lt.normalize(),e.setXYZ(t,Lt.x,Lt.y,Lt.z)}toNonIndexed(){function e(a,l){const c=a.array,u=a.itemSize,d=a.normalized,p=new c.constructor(l.length*u);let f=0,_=0;for(let g=0,m=l.length;g<m;g++){a.isInterleavedBufferAttribute?f=l[g]*a.data.stride+a.offset:f=l[g]*u;for(let h=0;h<u;h++)p[_++]=c[f++]}return new Zn(p,u,d)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new yi,i=this.index.array,r=this.attributes;for(const a in r){const l=r[a],c=e(l,i);t.setAttribute(a,c)}const s=this.morphAttributes;for(const a in s){const l=[],c=s[a];for(let u=0,d=c.length;u<d;u++){const p=c[u],f=e(p,i);l.push(f)}t.morphAttributes[a]=l}t.morphTargetsRelative=this.morphTargetsRelative;const o=this.groups;for(let a=0,l=o.length;a<l;a++){const c=o[a];t.addGroup(c.start,c.count,c.materialIndex)}return t}toJSON(){const e={metadata:{version:4.7,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const l=this.parameters;for(const c in l)l[c]!==void 0&&(e[c]=l[c]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const i=this.attributes;for(const l in i){const c=i[l];e.data.attributes[l]=c.toJSON(e.data)}const r={};let s=!1;for(const l in this.morphAttributes){const c=this.morphAttributes[l],u=[];for(let d=0,p=c.length;d<p;d++){const f=c[d];u.push(f.toJSON(e.data))}u.length>0&&(r[l]=u,s=!0)}s&&(e.data.morphAttributes=r,e.data.morphTargetsRelative=this.morphTargetsRelative);const o=this.groups;o.length>0&&(e.data.groups=JSON.parse(JSON.stringify(o)));const a=this.boundingSphere;return a!==null&&(e.data.boundingSphere=a.toJSON()),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const i=e.index;i!==null&&this.setIndex(i.clone());const r=e.attributes;for(const c in r){const u=r[c];this.setAttribute(c,u.clone(t))}const s=e.morphAttributes;for(const c in s){const u=[],d=s[c];for(let p=0,f=d.length;p<f;p++)u.push(d[p].clone(t));this.morphAttributes[c]=u}this.morphTargetsRelative=e.morphTargetsRelative;const o=e.groups;for(let c=0,u=o.length;c<u;c++){const d=o[c];this.addGroup(d.start,d.count,d.materialIndex)}const a=e.boundingBox;a!==null&&(this.boundingBox=a.clone());const l=e.boundingSphere;return l!==null&&(this.boundingSphere=l.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const gh=new Tt,Zi=new Ku,Oo=new za,_h=new B,Fo=new B,No=new B,ko=new B,Dl=new B,Bo=new B,vh=new B,zo=new B;class jn extends tn{constructor(e=new yi,t=new tm){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.morphTargetDictionary=void 0,this.morphTargetInfluences=void 0,this.count=1,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,i=Object.keys(t);if(i.length>0){const r=t[i[0]];if(r!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,o=r.length;s<o;s++){const a=r[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=s}}}}getVertexPosition(e,t){const i=this.geometry,r=i.attributes.position,s=i.morphAttributes.position,o=i.morphTargetsRelative;t.fromBufferAttribute(r,e);const a=this.morphTargetInfluences;if(s&&a){Bo.set(0,0,0);for(let l=0,c=s.length;l<c;l++){const u=a[l],d=s[l];u!==0&&(Dl.fromBufferAttribute(d,e),o?Bo.addScaledVector(Dl,u):Bo.addScaledVector(Dl.sub(t),u))}t.add(Bo)}return t}raycast(e,t){const i=this.geometry,r=this.material,s=this.matrixWorld;r!==void 0&&(i.boundingSphere===null&&i.computeBoundingSphere(),Oo.copy(i.boundingSphere),Oo.applyMatrix4(s),Zi.copy(e.ray).recast(e.near),!(Oo.containsPoint(Zi.origin)===!1&&(Zi.intersectSphere(Oo,_h)===null||Zi.origin.distanceToSquared(_h)>(e.far-e.near)**2))&&(gh.copy(s).invert(),Zi.copy(e.ray).applyMatrix4(gh),!(i.boundingBox!==null&&Zi.intersectsBox(i.boundingBox)===!1)&&this._computeIntersections(e,t,Zi)))}_computeIntersections(e,t,i){let r;const s=this.geometry,o=this.material,a=s.index,l=s.attributes.position,c=s.attributes.uv,u=s.attributes.uv1,d=s.attributes.normal,p=s.groups,f=s.drawRange;if(a!==null)if(Array.isArray(o))for(let _=0,g=p.length;_<g;_++){const m=p[_],h=o[m.materialIndex],v=Math.max(m.start,f.start),x=Math.min(a.count,Math.min(m.start+m.count,f.start+f.count));for(let w=v,S=x;w<S;w+=3){const C=a.getX(w),T=a.getX(w+1),A=a.getX(w+2);r=Vo(this,h,e,i,c,u,d,C,T,A),r&&(r.faceIndex=Math.floor(w/3),r.face.materialIndex=m.materialIndex,t.push(r))}}else{const _=Math.max(0,f.start),g=Math.min(a.count,f.start+f.count);for(let m=_,h=g;m<h;m+=3){const v=a.getX(m),x=a.getX(m+1),w=a.getX(m+2);r=Vo(this,o,e,i,c,u,d,v,x,w),r&&(r.faceIndex=Math.floor(m/3),t.push(r))}}else if(l!==void 0)if(Array.isArray(o))for(let _=0,g=p.length;_<g;_++){const m=p[_],h=o[m.materialIndex],v=Math.max(m.start,f.start),x=Math.min(l.count,Math.min(m.start+m.count,f.start+f.count));for(let w=v,S=x;w<S;w+=3){const C=w,T=w+1,A=w+2;r=Vo(this,h,e,i,c,u,d,C,T,A),r&&(r.faceIndex=Math.floor(w/3),r.face.materialIndex=m.materialIndex,t.push(r))}}else{const _=Math.max(0,f.start),g=Math.min(l.count,f.start+f.count);for(let m=_,h=g;m<h;m+=3){const v=m,x=m+1,w=m+2;r=Vo(this,o,e,i,c,u,d,v,x,w),r&&(r.faceIndex=Math.floor(m/3),t.push(r))}}}}function eb(n,e,t,i,r,s,o,a){let l;if(e.side===qt?l=i.intersectTriangle(o,s,r,!0,a):l=i.intersectTriangle(r,s,o,e.side===Hi,a),l===null)return null;zo.copy(a),zo.applyMatrix4(n.matrixWorld);const c=t.ray.origin.distanceTo(zo);return c<t.near||c>t.far?null:{distance:c,point:zo.clone(),object:n}}function Vo(n,e,t,i,r,s,o,a,l,c){n.getVertexPosition(a,Fo),n.getVertexPosition(l,No),n.getVertexPosition(c,ko);const u=eb(n,e,t,i,Fo,No,ko,vh);if(u){const d=new B;Fn.getBarycoord(vh,Fo,No,ko,d),r&&(u.uv=Fn.getInterpolatedAttribute(r,a,l,c,d,new Be)),s&&(u.uv1=Fn.getInterpolatedAttribute(s,a,l,c,d,new Be)),o&&(u.normal=Fn.getInterpolatedAttribute(o,a,l,c,d,new B),u.normal.dot(i.direction)>0&&u.normal.multiplyScalar(-1));const p={a,b:l,c,normal:new B,materialIndex:0};Fn.getNormal(Fo,No,ko,p.normal),u.face=p,u.barycoord=d}return u}class Ss extends yi{constructor(e=1,t=1,i=1,r=1,s=1,o=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:i,widthSegments:r,heightSegments:s,depthSegments:o};const a=this;r=Math.floor(r),s=Math.floor(s),o=Math.floor(o);const l=[],c=[],u=[],d=[];let p=0,f=0;_("z","y","x",-1,-1,i,t,e,o,s,0),_("z","y","x",1,-1,i,t,-e,o,s,1),_("x","z","y",1,1,e,i,t,r,o,2),_("x","z","y",1,-1,e,i,-t,r,o,3),_("x","y","z",1,-1,e,t,i,r,s,4),_("x","y","z",-1,-1,e,t,-i,r,s,5),this.setIndex(l),this.setAttribute("position",new Jn(c,3)),this.setAttribute("normal",new Jn(u,3)),this.setAttribute("uv",new Jn(d,2));function _(g,m,h,v,x,w,S,C,T,A,b){const y=w/T,P=S/A,D=w/2,O=S/2,V=C/2,k=T+1,G=A+1;let $=0,U=0;const Z=new B;for(let ee=0;ee<G;ee++){const ce=ee*P-O;for(let Ae=0;Ae<k;Ae++){const Je=Ae*y-D;Z[g]=Je*v,Z[m]=ce*x,Z[h]=V,c.push(Z.x,Z.y,Z.z),Z[g]=0,Z[m]=0,Z[h]=C>0?1:-1,u.push(Z.x,Z.y,Z.z),d.push(Ae/T),d.push(1-ee/A),$+=1}}for(let ee=0;ee<A;ee++)for(let ce=0;ce<T;ce++){const Ae=p+ce+k*ee,Je=p+ce+k*(ee+1),We=p+(ce+1)+k*(ee+1),ze=p+(ce+1)+k*ee;l.push(Ae,Je,ze),l.push(Je,We,ze),U+=6}a.addGroup(f,U,b),f+=U,p+=$}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Ss(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function cs(n){const e={};for(const t in n){e[t]={};for(const i in n[t]){const r=n[t][i];r&&(r.isColor||r.isMatrix3||r.isMatrix4||r.isVector2||r.isVector3||r.isVector4||r.isTexture||r.isQuaternion)?r.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][i]=null):e[t][i]=r.clone():Array.isArray(r)?e[t][i]=r.slice():e[t][i]=r}}return e}function Xt(n){const e={};for(let t=0;t<n.length;t++){const i=cs(n[t]);for(const r in i)e[r]=i[r]}return e}function tb(n){const e=[];for(let t=0;t<n.length;t++)e.push(n[t].clone());return e}function rm(n){const e=n.getRenderTarget();return e===null?n.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:qe.workingColorSpace}const sm={clone:cs,merge:Xt};var nb=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,ib=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class ti extends vo{constructor(e){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=nb,this.fragmentShader=ib,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=cs(e.uniforms),this.uniformsGroups=tb(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const r in this.uniforms){const o=this.uniforms[r].value;o&&o.isTexture?t.uniforms[r]={type:"t",value:o.toJSON(e).uuid}:o&&o.isColor?t.uniforms[r]={type:"c",value:o.getHex()}:o&&o.isVector2?t.uniforms[r]={type:"v2",value:o.toArray()}:o&&o.isVector3?t.uniforms[r]={type:"v3",value:o.toArray()}:o&&o.isVector4?t.uniforms[r]={type:"v4",value:o.toArray()}:o&&o.isMatrix3?t.uniforms[r]={type:"m3",value:o.toArray()}:o&&o.isMatrix4?t.uniforms[r]={type:"m4",value:o.toArray()}:t.uniforms[r]={value:o}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const i={};for(const r in this.extensions)this.extensions[r]===!0&&(i[r]=!0);return Object.keys(i).length>0&&(t.extensions=i),t}}class om extends tn{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new Tt,this.projectionMatrix=new Tt,this.projectionMatrixInverse=new Tt,this.coordinateSystem=Yn,this._reversedDepth=!1}get reversedDepth(){return this._reversedDepth}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const Ai=new B,xh=new Be,wh=new Be;class Cn extends om{constructor(e=50,t=1,i=.1,r=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=i,this.far=r,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=Ks*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(ks*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return Ks*2*Math.atan(Math.tan(ks*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,i){Ai.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(Ai.x,Ai.y).multiplyScalar(-e/Ai.z),Ai.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),i.set(Ai.x,Ai.y).multiplyScalar(-e/Ai.z)}getViewSize(e,t){return this.getViewBounds(e,xh,wh),t.subVectors(wh,xh)}setViewOffset(e,t,i,r,s,o){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=i,this.view.offsetY=r,this.view.width=s,this.view.height=o,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(ks*.5*this.fov)/this.zoom,i=2*t,r=this.aspect*i,s=-.5*r;const o=this.view;if(this.view!==null&&this.view.enabled){const l=o.fullWidth,c=o.fullHeight;s+=o.offsetX*r/l,t-=o.offsetY*i/c,r*=o.width/l,i*=o.height/c}const a=this.filmOffset;a!==0&&(s+=e*a/this.getFilmWidth()),this.projectionMatrix.makePerspective(s,s+r,t,t-i,e,this.far,this.coordinateSystem,this.reversedDepth),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const kr=-90,Br=1;class rb extends tn{constructor(e,t,i){super(),this.type="CubeCamera",this.renderTarget=i,this.coordinateSystem=null,this.activeMipmapLevel=0;const r=new Cn(kr,Br,e,t);r.layers=this.layers,this.add(r);const s=new Cn(kr,Br,e,t);s.layers=this.layers,this.add(s);const o=new Cn(kr,Br,e,t);o.layers=this.layers,this.add(o);const a=new Cn(kr,Br,e,t);a.layers=this.layers,this.add(a);const l=new Cn(kr,Br,e,t);l.layers=this.layers,this.add(l);const c=new Cn(kr,Br,e,t);c.layers=this.layers,this.add(c)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[i,r,s,o,a,l]=t;for(const c of t)this.remove(c);if(e===Yn)i.up.set(0,1,0),i.lookAt(1,0,0),r.up.set(0,1,0),r.lookAt(-1,0,0),s.up.set(0,0,-1),s.lookAt(0,1,0),o.up.set(0,0,1),o.lookAt(0,-1,0),a.up.set(0,1,0),a.lookAt(0,0,1),l.up.set(0,1,0),l.lookAt(0,0,-1);else if(e===Sa)i.up.set(0,-1,0),i.lookAt(-1,0,0),r.up.set(0,-1,0),r.lookAt(1,0,0),s.up.set(0,0,1),s.lookAt(0,1,0),o.up.set(0,0,-1),o.lookAt(0,-1,0),a.up.set(0,-1,0),a.lookAt(0,0,1),l.up.set(0,-1,0),l.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const c of t)this.add(c),c.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:i,activeMipmapLevel:r}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[s,o,a,l,c,u]=this.children,d=e.getRenderTarget(),p=e.getActiveCubeFace(),f=e.getActiveMipmapLevel(),_=e.xr.enabled;e.xr.enabled=!1;const g=i.texture.generateMipmaps;i.texture.generateMipmaps=!1,e.setRenderTarget(i,0,r),e.render(t,s),e.setRenderTarget(i,1,r),e.render(t,o),e.setRenderTarget(i,2,r),e.render(t,a),e.setRenderTarget(i,3,r),e.render(t,l),e.setRenderTarget(i,4,r),e.render(t,c),i.texture.generateMipmaps=g,e.setRenderTarget(i,5,r),e.render(t,u),e.setRenderTarget(d,p,f),e.xr.enabled=_,i.texture.needsPMREMUpdate=!0}}class am extends Yt{constructor(e=[],t=os,i,r,s,o,a,l,c,u){super(e,t,i,r,s,o,a,l,c,u),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class sb extends xr{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const i={width:e,height:e,depth:1},r=[i,i,i,i,i,i];this.texture=new am(r),this._setTextureOptions(t),this.texture.isRenderTargetTexture=!0}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const i={uniforms:{tEquirect:{value:null}},vertexShader:`

				varying vec3 vWorldDirection;

				vec3 transformDirection( in vec3 dir, in mat4 matrix ) {

					return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );

				}

				void main() {

					vWorldDirection = transformDirection( position, modelMatrix );

					#include <begin_vertex>
					#include <project_vertex>

				}
			`,fragmentShader:`

				uniform sampler2D tEquirect;

				varying vec3 vWorldDirection;

				#include <common>

				void main() {

					vec3 direction = normalize( vWorldDirection );

					vec2 sampleUV = equirectUv( direction );

					gl_FragColor = texture2D( tEquirect, sampleUV );

				}
			`},r=new Ss(5,5,5),s=new ti({name:"CubemapFromEquirect",uniforms:cs(i.uniforms),vertexShader:i.vertexShader,fragmentShader:i.fragmentShader,side:qt,blending:ki});s.uniforms.tEquirect.value=t;const o=new jn(r,s),a=t.minFilter;return t.minFilter===cr&&(t.minFilter=qn),new rb(1,10,this).update(e,o),t.minFilter=a,o.geometry.dispose(),o.material.dispose(),this}clear(e,t=!0,i=!0,r=!0){const s=e.getRenderTarget();for(let o=0;o<6;o++)e.setRenderTarget(this,o),e.clear(t,i,r);e.setRenderTarget(s)}}class Ho extends tn{constructor(){super(),this.isGroup=!0,this.type="Group"}}const ob={type:"move"};class Ll{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new Ho,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new Ho,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new B,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new B),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new Ho,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new B,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new B),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const i of e.hand.values())this._getHandJoint(t,i)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,i){let r=null,s=null,o=null;const a=this._targetRay,l=this._grip,c=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(c&&e.hand){o=!0;for(const g of e.hand.values()){const m=t.getJointPose(g,i),h=this._getHandJoint(c,g);m!==null&&(h.matrix.fromArray(m.transform.matrix),h.matrix.decompose(h.position,h.rotation,h.scale),h.matrixWorldNeedsUpdate=!0,h.jointRadius=m.radius),h.visible=m!==null}const u=c.joints["index-finger-tip"],d=c.joints["thumb-tip"],p=u.position.distanceTo(d.position),f=.02,_=.005;c.inputState.pinching&&p>f+_?(c.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!c.inputState.pinching&&p<=f-_&&(c.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else l!==null&&e.gripSpace&&(s=t.getPose(e.gripSpace,i),s!==null&&(l.matrix.fromArray(s.transform.matrix),l.matrix.decompose(l.position,l.rotation,l.scale),l.matrixWorldNeedsUpdate=!0,s.linearVelocity?(l.hasLinearVelocity=!0,l.linearVelocity.copy(s.linearVelocity)):l.hasLinearVelocity=!1,s.angularVelocity?(l.hasAngularVelocity=!0,l.angularVelocity.copy(s.angularVelocity)):l.hasAngularVelocity=!1));a!==null&&(r=t.getPose(e.targetRaySpace,i),r===null&&s!==null&&(r=s),r!==null&&(a.matrix.fromArray(r.transform.matrix),a.matrix.decompose(a.position,a.rotation,a.scale),a.matrixWorldNeedsUpdate=!0,r.linearVelocity?(a.hasLinearVelocity=!0,a.linearVelocity.copy(r.linearVelocity)):a.hasLinearVelocity=!1,r.angularVelocity?(a.hasAngularVelocity=!0,a.angularVelocity.copy(r.angularVelocity)):a.hasAngularVelocity=!1,this.dispatchEvent(ob)))}return a!==null&&(a.visible=r!==null),l!==null&&(l.visible=s!==null),c!==null&&(c.visible=o!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const i=new Ho;i.matrixAutoUpdate=!1,i.visible=!1,e.joints[t.jointName]=i,e.add(i)}return e.joints[t.jointName]}}class ab extends tn{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new vi,this.environmentIntensity=1,this.environmentRotation=new vi,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}const Il=new B,lb=new B,cb=new Fe;class Ci{constructor(e=new B(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,i,r){return this.normal.set(e,t,i),this.constant=r,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,i){const r=Il.subVectors(i,t).cross(lb.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(r,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const i=e.delta(Il),r=this.normal.dot(i);if(r===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const s=-(e.start.dot(this.normal)+this.constant)/r;return s<0||s>1?null:t.copy(e.start).addScaledVector(i,s)}intersectsLine(e){const t=this.distanceToPoint(e.start),i=this.distanceToPoint(e.end);return t<0&&i>0||i<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const i=t||cb.getNormalMatrix(e),r=this.coplanarPoint(Il).applyMatrix4(e),s=this.normal.applyMatrix3(i).normalize();return this.constant=-r.dot(s),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const Ji=new za,ub=new Be(.5,.5),Go=new B;class lm{constructor(e=new Ci,t=new Ci,i=new Ci,r=new Ci,s=new Ci,o=new Ci){this.planes=[e,t,i,r,s,o]}set(e,t,i,r,s,o){const a=this.planes;return a[0].copy(e),a[1].copy(t),a[2].copy(i),a[3].copy(r),a[4].copy(s),a[5].copy(o),this}copy(e){const t=this.planes;for(let i=0;i<6;i++)t[i].copy(e.planes[i]);return this}setFromProjectionMatrix(e,t=Yn,i=!1){const r=this.planes,s=e.elements,o=s[0],a=s[1],l=s[2],c=s[3],u=s[4],d=s[5],p=s[6],f=s[7],_=s[8],g=s[9],m=s[10],h=s[11],v=s[12],x=s[13],w=s[14],S=s[15];if(r[0].setComponents(c-o,f-u,h-_,S-v).normalize(),r[1].setComponents(c+o,f+u,h+_,S+v).normalize(),r[2].setComponents(c+a,f+d,h+g,S+x).normalize(),r[3].setComponents(c-a,f-d,h-g,S-x).normalize(),i)r[4].setComponents(l,p,m,w).normalize(),r[5].setComponents(c-l,f-p,h-m,S-w).normalize();else if(r[4].setComponents(c-l,f-p,h-m,S-w).normalize(),t===Yn)r[5].setComponents(c+l,f+p,h+m,S+w).normalize();else if(t===Sa)r[5].setComponents(l,p,m,w).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),Ji.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),Ji.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(Ji)}intersectsSprite(e){Ji.center.set(0,0,0);const t=ub.distanceTo(e.center);return Ji.radius=.7071067811865476+t,Ji.applyMatrix4(e.matrixWorld),this.intersectsSphere(Ji)}intersectsSphere(e){const t=this.planes,i=e.center,r=-e.radius;for(let s=0;s<6;s++)if(t[s].distanceToPoint(i)<r)return!1;return!0}intersectsBox(e){const t=this.planes;for(let i=0;i<6;i++){const r=t[i];if(Go.x=r.normal.x>0?e.max.x:e.min.x,Go.y=r.normal.y>0?e.max.y:e.min.y,Go.z=r.normal.z>0?e.max.z:e.min.z,r.distanceToPoint(Go)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let i=0;i<6;i++)if(t[i].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}class db extends vo{constructor(e){super(),this.isPointsMaterial=!0,this.type="PointsMaterial",this.color=new Ze(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const yh=new Tt,Zc=new Ku,Wo=new za,Xo=new B;class hb extends tn{constructor(e=new yi,t=new db){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.morphTargetDictionary=void 0,this.morphTargetInfluences=void 0,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const i=this.geometry,r=this.matrixWorld,s=e.params.Points.threshold,o=i.drawRange;if(i.boundingSphere===null&&i.computeBoundingSphere(),Wo.copy(i.boundingSphere),Wo.applyMatrix4(r),Wo.radius+=s,e.ray.intersectsSphere(Wo)===!1)return;yh.copy(r).invert(),Zc.copy(e.ray).applyMatrix4(yh);const a=s/((this.scale.x+this.scale.y+this.scale.z)/3),l=a*a,c=i.index,d=i.attributes.position;if(c!==null){const p=Math.max(0,o.start),f=Math.min(c.count,o.start+o.count);for(let _=p,g=f;_<g;_++){const m=c.getX(_);Xo.fromBufferAttribute(d,m),bh(Xo,m,l,r,e,t,this)}}else{const p=Math.max(0,o.start),f=Math.min(d.count,o.start+o.count);for(let _=p,g=f;_<g;_++)Xo.fromBufferAttribute(d,_),bh(Xo,_,l,r,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,i=Object.keys(t);if(i.length>0){const r=t[i[0]];if(r!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,o=r.length;s<o;s++){const a=r[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=s}}}}}function bh(n,e,t,i,r,s,o){const a=Zc.distanceSqToPoint(n);if(a<t){const l=new B;Zc.closestPointToPoint(n,l),l.applyMatrix4(i);const c=r.ray.origin.distanceTo(l);if(c<r.near||c>r.far)return;s.push({distance:c,distanceToRay:Math.sqrt(a),point:l,index:e,face:null,faceIndex:null,barycoord:null,object:o})}}class cm extends Yt{constructor(e,t,i=_r,r,s,o,a=kn,l=kn,c,u=Ys,d=1){if(u!==Ys&&u!==js)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");const p={width:e,height:t,depth:d};super(p,r,s,o,a,l,u,i,c),this.isDepthTexture=!0,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.source=new ju(Object.assign({},e.image)),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}class um extends Yt{constructor(e=null){super(),this.sourceTexture=e,this.isExternalTexture=!0}copy(e){return super.copy(e),this.sourceTexture=e.sourceTexture,this}}class Va extends yi{constructor(e=1,t=1,i=1,r=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:i,heightSegments:r};const s=e/2,o=t/2,a=Math.floor(i),l=Math.floor(r),c=a+1,u=l+1,d=e/a,p=t/l,f=[],_=[],g=[],m=[];for(let h=0;h<u;h++){const v=h*p-o;for(let x=0;x<c;x++){const w=x*d-s;_.push(w,-v,0),g.push(0,0,1),m.push(x/a),m.push(1-h/l)}}for(let h=0;h<l;h++)for(let v=0;v<a;v++){const x=v+c*h,w=v+c*(h+1),S=v+1+c*(h+1),C=v+1+c*h;f.push(x,w,C),f.push(w,S,C)}this.setIndex(f),this.setAttribute("position",new Jn(_,3)),this.setAttribute("normal",new Jn(g,3)),this.setAttribute("uv",new Jn(m,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Va(e.width,e.height,e.widthSegments,e.heightSegments)}}class fb extends vo{constructor(e){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=cy,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class pb extends vo{constructor(e){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const Ul={enabled:!1,files:{},add:function(n,e){this.enabled!==!1&&(this.files[n]=e)},get:function(n){if(this.enabled!==!1)return this.files[n]},remove:function(n){delete this.files[n]},clear:function(){this.files={}}};class mb{constructor(e,t,i){const r=this;let s=!1,o=0,a=0,l;const c=[];this.onStart=void 0,this.onLoad=e,this.onProgress=t,this.onError=i,this.abortController=new AbortController,this.itemStart=function(u){a++,s===!1&&r.onStart!==void 0&&r.onStart(u,o,a),s=!0},this.itemEnd=function(u){o++,r.onProgress!==void 0&&r.onProgress(u,o,a),o===a&&(s=!1,r.onLoad!==void 0&&r.onLoad())},this.itemError=function(u){r.onError!==void 0&&r.onError(u)},this.resolveURL=function(u){return l?l(u):u},this.setURLModifier=function(u){return l=u,this},this.addHandler=function(u,d){return c.push(u,d),this},this.removeHandler=function(u){const d=c.indexOf(u);return d!==-1&&c.splice(d,2),this},this.getHandler=function(u){for(let d=0,p=c.length;d<p;d+=2){const f=c[d],_=c[d+1];if(f.global&&(f.lastIndex=0),f.test(u))return _}return null},this.abort=function(){return this.abortController.abort(),this.abortController=new AbortController,this}}}const gb=new mb;class Zu{constructor(e){this.manager=e!==void 0?e:gb,this.crossOrigin="anonymous",this.withCredentials=!1,this.path="",this.resourcePath="",this.requestHeader={}}load(){}loadAsync(e,t){const i=this;return new Promise(function(r,s){i.load(e,r,t,s)})}parse(){}setCrossOrigin(e){return this.crossOrigin=e,this}setWithCredentials(e){return this.withCredentials=e,this}setPath(e){return this.path=e,this}setResourcePath(e){return this.resourcePath=e,this}setRequestHeader(e){return this.requestHeader=e,this}abort(){return this}}Zu.DEFAULT_MATERIAL_NAME="__DEFAULT";const zr=new WeakMap;class _b extends Zu{constructor(e){super(e)}load(e,t,i,r){this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=this,o=Ul.get(`image:${e}`);if(o!==void 0){if(o.complete===!0)s.manager.itemStart(e),setTimeout(function(){t&&t(o),s.manager.itemEnd(e)},0);else{let d=zr.get(o);d===void 0&&(d=[],zr.set(o,d)),d.push({onLoad:t,onError:r})}return o}const a=Zs("img");function l(){u(),t&&t(this);const d=zr.get(this)||[];for(let p=0;p<d.length;p++){const f=d[p];f.onLoad&&f.onLoad(this)}zr.delete(this),s.manager.itemEnd(e)}function c(d){u(),r&&r(d),Ul.remove(`image:${e}`);const p=zr.get(this)||[];for(let f=0;f<p.length;f++){const _=p[f];_.onError&&_.onError(d)}zr.delete(this),s.manager.itemError(e),s.manager.itemEnd(e)}function u(){a.removeEventListener("load",l,!1),a.removeEventListener("error",c,!1)}return a.addEventListener("load",l,!1),a.addEventListener("error",c,!1),e.slice(0,5)!=="data:"&&this.crossOrigin!==void 0&&(a.crossOrigin=this.crossOrigin),Ul.add(`image:${e}`,a),s.manager.itemStart(e),a.src=e,a}}class vb extends Zu{constructor(e){super(e)}load(e,t,i,r){const s=new Yt,o=new _b(this.manager);return o.setCrossOrigin(this.crossOrigin),o.setPath(this.path),o.load(e,function(a){s.image=a,s.needsUpdate=!0,t!==void 0&&t(s)},i,r),s}}class xb extends om{constructor(e=-1,t=1,i=1,r=-1,s=.1,o=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=i,this.bottom=r,this.near=s,this.far=o,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,i,r,s,o){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=i,this.view.offsetY=r,this.view.width=s,this.view.height=o,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),i=(this.right+this.left)/2,r=(this.top+this.bottom)/2;let s=i-e,o=i+e,a=r+t,l=r-t;if(this.view!==null&&this.view.enabled){const c=(this.right-this.left)/this.view.fullWidth/this.zoom,u=(this.top-this.bottom)/this.view.fullHeight/this.zoom;s+=c*this.view.offsetX,o=s+c*this.view.width,a-=u*this.view.offsetY,l=a-u*this.view.height}this.projectionMatrix.makeOrthographic(s,o,a,l,this.near,this.far,this.coordinateSystem,this.reversedDepth),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}class wb extends Cn{constructor(e=[]){super(),this.isArrayCamera=!0,this.isMultiViewCamera=!1,this.cameras=e}}class or{constructor(e){this.value=e}clone(){return new or(this.value.clone===void 0?this.value:this.value.clone())}}class Jc{constructor(e=1,t=0,i=0){this.radius=e,this.phi=t,this.theta=i}set(e,t,i){return this.radius=e,this.phi=t,this.theta=i,this}copy(e){return this.radius=e.radius,this.phi=e.phi,this.theta=e.theta,this}makeSafe(){return this.phi=Ve(this.phi,1e-6,Math.PI-1e-6),this}setFromVector3(e){return this.setFromCartesianCoords(e.x,e.y,e.z)}setFromCartesianCoords(e,t,i){return this.radius=Math.sqrt(e*e+t*t+i*i),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(e,i),this.phi=Math.acos(Ve(t/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}}class yb extends Er{constructor(e,t=null){super(),this.object=e,this.domElement=t,this.enabled=!0,this.state=-1,this.keys={},this.mouseButtons={LEFT:null,MIDDLE:null,RIGHT:null},this.touches={ONE:null,TWO:null}}connect(e){if(e===void 0){console.warn("THREE.Controls: connect() now requires an element.");return}this.domElement!==null&&this.disconnect(),this.domElement=e}disconnect(){}dispose(){}update(){}}function Sh(n,e,t,i){const r=bb(i);switch(t){case $p:return n*e;case Yp:return n*e/r.components*r.byteLength;case Xu:return n*e/r.components*r.byteLength;case jp:return n*e*2/r.components*r.byteLength;case $u:return n*e*2/r.components*r.byteLength;case qp:return n*e*3/r.components*r.byteLength;case Nn:return n*e*4/r.components*r.byteLength;case qu:return n*e*4/r.components*r.byteLength;case Qo:case ea:return Math.floor((n+3)/4)*Math.floor((e+3)/4)*8;case ta:case na:return Math.floor((n+3)/4)*Math.floor((e+3)/4)*16;case Sc:case Mc:return Math.max(n,16)*Math.max(e,8)/4;case bc:case Ec:return Math.max(n,8)*Math.max(e,8)/2;case Tc:case Ac:return Math.floor((n+3)/4)*Math.floor((e+3)/4)*8;case Cc:return Math.floor((n+3)/4)*Math.floor((e+3)/4)*16;case Pc:return Math.floor((n+3)/4)*Math.floor((e+3)/4)*16;case Rc:return Math.floor((n+4)/5)*Math.floor((e+3)/4)*16;case Dc:return Math.floor((n+4)/5)*Math.floor((e+4)/5)*16;case Lc:return Math.floor((n+5)/6)*Math.floor((e+4)/5)*16;case Ic:return Math.floor((n+5)/6)*Math.floor((e+5)/6)*16;case Uc:return Math.floor((n+7)/8)*Math.floor((e+4)/5)*16;case Oc:return Math.floor((n+7)/8)*Math.floor((e+5)/6)*16;case Fc:return Math.floor((n+7)/8)*Math.floor((e+7)/8)*16;case Nc:return Math.floor((n+9)/10)*Math.floor((e+4)/5)*16;case kc:return Math.floor((n+9)/10)*Math.floor((e+5)/6)*16;case Bc:return Math.floor((n+9)/10)*Math.floor((e+7)/8)*16;case zc:return Math.floor((n+9)/10)*Math.floor((e+9)/10)*16;case Vc:return Math.floor((n+11)/12)*Math.floor((e+9)/10)*16;case Hc:return Math.floor((n+11)/12)*Math.floor((e+11)/12)*16;case Gc:case Wc:case Xc:return Math.ceil(n/4)*Math.ceil(e/4)*16;case $c:case qc:return Math.ceil(n/4)*Math.ceil(e/4)*8;case Yc:case jc:return Math.ceil(n/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function bb(n){switch(n){case _i:case Hp:return{byteLength:1,components:1};case $s:case Gp:case go:return{byteLength:2,components:1};case Gu:case Wu:return{byteLength:2,components:4};case _r:case Hu:case fi:return{byteLength:4,components:1};case Wp:case Xp:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${n}.`)}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:Vu}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=Vu);/**
 * @license
 * Copyright 2010-2025 Three.js Authors
 * SPDX-License-Identifier: MIT
 */function dm(){let n=null,e=!1,t=null,i=null;function r(s,o){t(s,o),i=n.requestAnimationFrame(r)}return{start:function(){e!==!0&&t!==null&&(i=n.requestAnimationFrame(r),e=!0)},stop:function(){n.cancelAnimationFrame(i),e=!1},setAnimationLoop:function(s){t=s},setContext:function(s){n=s}}}function Sb(n){const e=new WeakMap;function t(a,l){const c=a.array,u=a.usage,d=c.byteLength,p=n.createBuffer();n.bindBuffer(l,p),n.bufferData(l,c,u),a.onUploadCallback();let f;if(c instanceof Float32Array)f=n.FLOAT;else if(typeof Float16Array<"u"&&c instanceof Float16Array)f=n.HALF_FLOAT;else if(c instanceof Uint16Array)a.isFloat16BufferAttribute?f=n.HALF_FLOAT:f=n.UNSIGNED_SHORT;else if(c instanceof Int16Array)f=n.SHORT;else if(c instanceof Uint32Array)f=n.UNSIGNED_INT;else if(c instanceof Int32Array)f=n.INT;else if(c instanceof Int8Array)f=n.BYTE;else if(c instanceof Uint8Array)f=n.UNSIGNED_BYTE;else if(c instanceof Uint8ClampedArray)f=n.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+c);return{buffer:p,type:f,bytesPerElement:c.BYTES_PER_ELEMENT,version:a.version,size:d}}function i(a,l,c){const u=l.array,d=l.updateRanges;if(n.bindBuffer(c,a),d.length===0)n.bufferSubData(c,0,u);else{d.sort((f,_)=>f.start-_.start);let p=0;for(let f=1;f<d.length;f++){const _=d[p],g=d[f];g.start<=_.start+_.count+1?_.count=Math.max(_.count,g.start+g.count-_.start):(++p,d[p]=g)}d.length=p+1;for(let f=0,_=d.length;f<_;f++){const g=d[f];n.bufferSubData(c,g.start*u.BYTES_PER_ELEMENT,u,g.start,g.count)}l.clearUpdateRanges()}l.onUploadCallback()}function r(a){return a.isInterleavedBufferAttribute&&(a=a.data),e.get(a)}function s(a){a.isInterleavedBufferAttribute&&(a=a.data);const l=e.get(a);l&&(n.deleteBuffer(l.buffer),e.delete(a))}function o(a,l){if(a.isInterleavedBufferAttribute&&(a=a.data),a.isGLBufferAttribute){const u=e.get(a);(!u||u.version<a.version)&&e.set(a,{buffer:a.buffer,type:a.type,bytesPerElement:a.elementSize,version:a.version});return}const c=e.get(a);if(c===void 0)e.set(a,t(a,l));else if(c.version<a.version){if(c.size!==a.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");i(c.buffer,a,l),c.version=a.version}}return{get:r,remove:s,update:o}}var Eb=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,Mb=`#ifdef USE_ALPHAHASH
	const float ALPHA_HASH_SCALE = 0.05;
	float hash2D( vec2 value ) {
		return fract( 1.0e4 * sin( 17.0 * value.x + 0.1 * value.y ) * ( 0.1 + abs( sin( 13.0 * value.y + value.x ) ) ) );
	}
	float hash3D( vec3 value ) {
		return hash2D( vec2( hash2D( value.xy ), value.z ) );
	}
	float getAlphaHashThreshold( vec3 position ) {
		float maxDeriv = max(
			length( dFdx( position.xyz ) ),
			length( dFdy( position.xyz ) )
		);
		float pixScale = 1.0 / ( ALPHA_HASH_SCALE * maxDeriv );
		vec2 pixScales = vec2(
			exp2( floor( log2( pixScale ) ) ),
			exp2( ceil( log2( pixScale ) ) )
		);
		vec2 alpha = vec2(
			hash3D( floor( pixScales.x * position.xyz ) ),
			hash3D( floor( pixScales.y * position.xyz ) )
		);
		float lerpFactor = fract( log2( pixScale ) );
		float x = ( 1.0 - lerpFactor ) * alpha.x + lerpFactor * alpha.y;
		float a = min( lerpFactor, 1.0 - lerpFactor );
		vec3 cases = vec3(
			x * x / ( 2.0 * a * ( 1.0 - a ) ),
			( x - 0.5 * a ) / ( 1.0 - a ),
			1.0 - ( ( 1.0 - x ) * ( 1.0 - x ) / ( 2.0 * a * ( 1.0 - a ) ) )
		);
		float threshold = ( x < ( 1.0 - a ) )
			? ( ( x < a ) ? cases.x : cases.y )
			: cases.z;
		return clamp( threshold , 1.0e-6, 1.0 );
	}
#endif`,Tb=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,Ab=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,Cb=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,Pb=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,Rb=`#ifdef USE_AOMAP
	float ambientOcclusion = ( texture2D( aoMap, vAoMapUv ).r - 1.0 ) * aoMapIntensity + 1.0;
	reflectedLight.indirectDiffuse *= ambientOcclusion;
	#if defined( USE_CLEARCOAT ) 
		clearcoatSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_SHEEN ) 
		sheenSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD )
		float dotNV = saturate( dot( geometryNormal, geometryViewDir ) );
		reflectedLight.indirectSpecular *= computeSpecularOcclusion( dotNV, ambientOcclusion, material.roughness );
	#endif
#endif`,Db=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,Lb=`#ifdef USE_BATCHING
	#if ! defined( GL_ANGLE_multi_draw )
	#define gl_DrawID _gl_DrawID
	uniform int _gl_DrawID;
	#endif
	uniform highp sampler2D batchingTexture;
	uniform highp usampler2D batchingIdTexture;
	mat4 getBatchingMatrix( const in float i ) {
		int size = textureSize( batchingTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( batchingTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( batchingTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( batchingTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( batchingTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
	float getIndirectIndex( const in int i ) {
		int size = textureSize( batchingIdTexture, 0 ).x;
		int x = i % size;
		int y = i / size;
		return float( texelFetch( batchingIdTexture, ivec2( x, y ), 0 ).r );
	}
#endif
#ifdef USE_BATCHING_COLOR
	uniform sampler2D batchingColorTexture;
	vec3 getBatchingColor( const in float i ) {
		int size = textureSize( batchingColorTexture, 0 ).x;
		int j = int( i );
		int x = j % size;
		int y = j / size;
		return texelFetch( batchingColorTexture, ivec2( x, y ), 0 ).rgb;
	}
#endif`,Ib=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,Ub=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,Ob=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,Fb=`float G_BlinnPhong_Implicit( ) {
	return 0.25;
}
float D_BlinnPhong( const in float shininess, const in float dotNH ) {
	return RECIPROCAL_PI * ( shininess * 0.5 + 1.0 ) * pow( dotNH, shininess );
}
vec3 BRDF_BlinnPhong( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in vec3 specularColor, const in float shininess ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( specularColor, 1.0, dotVH );
	float G = G_BlinnPhong_Implicit( );
	float D = D_BlinnPhong( shininess, dotNH );
	return F * ( G * D );
} // validated`,Nb=`#ifdef USE_IRIDESCENCE
	const mat3 XYZ_TO_REC709 = mat3(
		 3.2404542, -0.9692660,  0.0556434,
		-1.5371385,  1.8760108, -0.2040259,
		-0.4985314,  0.0415560,  1.0572252
	);
	vec3 Fresnel0ToIor( vec3 fresnel0 ) {
		vec3 sqrtF0 = sqrt( fresnel0 );
		return ( vec3( 1.0 ) + sqrtF0 ) / ( vec3( 1.0 ) - sqrtF0 );
	}
	vec3 IorToFresnel0( vec3 transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - vec3( incidentIor ) ) / ( transmittedIor + vec3( incidentIor ) ) );
	}
	float IorToFresnel0( float transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - incidentIor ) / ( transmittedIor + incidentIor ));
	}
	vec3 evalSensitivity( float OPD, vec3 shift ) {
		float phase = 2.0 * PI * OPD * 1.0e-9;
		vec3 val = vec3( 5.4856e-13, 4.4201e-13, 5.2481e-13 );
		vec3 pos = vec3( 1.6810e+06, 1.7953e+06, 2.2084e+06 );
		vec3 var = vec3( 4.3278e+09, 9.3046e+09, 6.6121e+09 );
		vec3 xyz = val * sqrt( 2.0 * PI * var ) * cos( pos * phase + shift ) * exp( - pow2( phase ) * var );
		xyz.x += 9.7470e-14 * sqrt( 2.0 * PI * 4.5282e+09 ) * cos( 2.2399e+06 * phase + shift[ 0 ] ) * exp( - 4.5282e+09 * pow2( phase ) );
		xyz /= 1.0685e-7;
		vec3 rgb = XYZ_TO_REC709 * xyz;
		return rgb;
	}
	vec3 evalIridescence( float outsideIOR, float eta2, float cosTheta1, float thinFilmThickness, vec3 baseF0 ) {
		vec3 I;
		float iridescenceIOR = mix( outsideIOR, eta2, smoothstep( 0.0, 0.03, thinFilmThickness ) );
		float sinTheta2Sq = pow2( outsideIOR / iridescenceIOR ) * ( 1.0 - pow2( cosTheta1 ) );
		float cosTheta2Sq = 1.0 - sinTheta2Sq;
		if ( cosTheta2Sq < 0.0 ) {
			return vec3( 1.0 );
		}
		float cosTheta2 = sqrt( cosTheta2Sq );
		float R0 = IorToFresnel0( iridescenceIOR, outsideIOR );
		float R12 = F_Schlick( R0, 1.0, cosTheta1 );
		float T121 = 1.0 - R12;
		float phi12 = 0.0;
		if ( iridescenceIOR < outsideIOR ) phi12 = PI;
		float phi21 = PI - phi12;
		vec3 baseIOR = Fresnel0ToIor( clamp( baseF0, 0.0, 0.9999 ) );		vec3 R1 = IorToFresnel0( baseIOR, iridescenceIOR );
		vec3 R23 = F_Schlick( R1, 1.0, cosTheta2 );
		vec3 phi23 = vec3( 0.0 );
		if ( baseIOR[ 0 ] < iridescenceIOR ) phi23[ 0 ] = PI;
		if ( baseIOR[ 1 ] < iridescenceIOR ) phi23[ 1 ] = PI;
		if ( baseIOR[ 2 ] < iridescenceIOR ) phi23[ 2 ] = PI;
		float OPD = 2.0 * iridescenceIOR * thinFilmThickness * cosTheta2;
		vec3 phi = vec3( phi21 ) + phi23;
		vec3 R123 = clamp( R12 * R23, 1e-5, 0.9999 );
		vec3 r123 = sqrt( R123 );
		vec3 Rs = pow2( T121 ) * R23 / ( vec3( 1.0 ) - R123 );
		vec3 C0 = R12 + Rs;
		I = C0;
		vec3 Cm = Rs - T121;
		for ( int m = 1; m <= 2; ++ m ) {
			Cm *= r123;
			vec3 Sm = 2.0 * evalSensitivity( float( m ) * OPD, float( m ) * phi );
			I += Cm * Sm;
		}
		return max( I, vec3( 0.0 ) );
	}
#endif`,kb=`#ifdef USE_BUMPMAP
	uniform sampler2D bumpMap;
	uniform float bumpScale;
	vec2 dHdxy_fwd() {
		vec2 dSTdx = dFdx( vBumpMapUv );
		vec2 dSTdy = dFdy( vBumpMapUv );
		float Hll = bumpScale * texture2D( bumpMap, vBumpMapUv ).x;
		float dBx = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdx ).x - Hll;
		float dBy = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdy ).x - Hll;
		return vec2( dBx, dBy );
	}
	vec3 perturbNormalArb( vec3 surf_pos, vec3 surf_norm, vec2 dHdxy, float faceDirection ) {
		vec3 vSigmaX = normalize( dFdx( surf_pos.xyz ) );
		vec3 vSigmaY = normalize( dFdy( surf_pos.xyz ) );
		vec3 vN = surf_norm;
		vec3 R1 = cross( vSigmaY, vN );
		vec3 R2 = cross( vN, vSigmaX );
		float fDet = dot( vSigmaX, R1 ) * faceDirection;
		vec3 vGrad = sign( fDet ) * ( dHdxy.x * R1 + dHdxy.y * R2 );
		return normalize( abs( fDet ) * surf_norm - vGrad );
	}
#endif`,Bb=`#if NUM_CLIPPING_PLANES > 0
	vec4 plane;
	#ifdef ALPHA_TO_COVERAGE
		float distanceToPlane, distanceGradient;
		float clipOpacity = 1.0;
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
			distanceGradient = fwidth( distanceToPlane ) / 2.0;
			clipOpacity *= smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			if ( clipOpacity == 0.0 ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			float unionClipOpacity = 1.0;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
				distanceGradient = fwidth( distanceToPlane ) / 2.0;
				unionClipOpacity *= 1.0 - smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			}
			#pragma unroll_loop_end
			clipOpacity *= 1.0 - unionClipOpacity;
		#endif
		diffuseColor.a *= clipOpacity;
		if ( diffuseColor.a == 0.0 ) discard;
	#else
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			if ( dot( vClipPosition, plane.xyz ) > plane.w ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			bool clipped = true;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				clipped = ( dot( vClipPosition, plane.xyz ) > plane.w ) && clipped;
			}
			#pragma unroll_loop_end
			if ( clipped ) discard;
		#endif
	#endif
#endif`,zb=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,Vb=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,Hb=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,Gb=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,Wb=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,Xb=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,$b=`#if defined( USE_COLOR_ALPHA )
	vColor = vec4( 1.0 );
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	vColor = vec3( 1.0 );
#endif
#ifdef USE_COLOR
	vColor *= color;
#endif
#ifdef USE_INSTANCING_COLOR
	vColor.xyz *= instanceColor.xyz;
#endif
#ifdef USE_BATCHING_COLOR
	vec3 batchingColor = getBatchingColor( getIndirectIndex( gl_DrawID ) );
	vColor.xyz *= batchingColor.xyz;
#endif`,qb=`#define PI 3.141592653589793
#define PI2 6.283185307179586
#define PI_HALF 1.5707963267948966
#define RECIPROCAL_PI 0.3183098861837907
#define RECIPROCAL_PI2 0.15915494309189535
#define EPSILON 1e-6
#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
#define whiteComplement( a ) ( 1.0 - saturate( a ) )
float pow2( const in float x ) { return x*x; }
vec3 pow2( const in vec3 x ) { return x*x; }
float pow3( const in float x ) { return x*x*x; }
float pow4( const in float x ) { float x2 = x*x; return x2*x2; }
float max3( const in vec3 v ) { return max( max( v.x, v.y ), v.z ); }
float average( const in vec3 v ) { return dot( v, vec3( 0.3333333 ) ); }
highp float rand( const in vec2 uv ) {
	const highp float a = 12.9898, b = 78.233, c = 43758.5453;
	highp float dt = dot( uv.xy, vec2( a,b ) ), sn = mod( dt, PI );
	return fract( sin( sn ) * c );
}
#ifdef HIGH_PRECISION
	float precisionSafeLength( vec3 v ) { return length( v ); }
#else
	float precisionSafeLength( vec3 v ) {
		float maxComponent = max3( abs( v ) );
		return length( v / maxComponent ) * maxComponent;
	}
#endif
struct IncidentLight {
	vec3 color;
	vec3 direction;
	bool visible;
};
struct ReflectedLight {
	vec3 directDiffuse;
	vec3 directSpecular;
	vec3 indirectDiffuse;
	vec3 indirectSpecular;
};
#ifdef USE_ALPHAHASH
	varying vec3 vPosition;
#endif
vec3 transformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );
}
vec3 inverseTransformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( vec4( dir, 0.0 ) * matrix ).xyz );
}
mat3 transposeMat3( const in mat3 m ) {
	mat3 tmp;
	tmp[ 0 ] = vec3( m[ 0 ].x, m[ 1 ].x, m[ 2 ].x );
	tmp[ 1 ] = vec3( m[ 0 ].y, m[ 1 ].y, m[ 2 ].y );
	tmp[ 2 ] = vec3( m[ 0 ].z, m[ 1 ].z, m[ 2 ].z );
	return tmp;
}
bool isPerspectiveMatrix( mat4 m ) {
	return m[ 2 ][ 3 ] == - 1.0;
}
vec2 equirectUv( in vec3 dir ) {
	float u = atan( dir.z, dir.x ) * RECIPROCAL_PI2 + 0.5;
	float v = asin( clamp( dir.y, - 1.0, 1.0 ) ) * RECIPROCAL_PI + 0.5;
	return vec2( u, v );
}
vec3 BRDF_Lambert( const in vec3 diffuseColor ) {
	return RECIPROCAL_PI * diffuseColor;
}
vec3 F_Schlick( const in vec3 f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
}
float F_Schlick( const in float f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
} // validated`,Yb=`#ifdef ENVMAP_TYPE_CUBE_UV
	#define cubeUV_minMipLevel 4.0
	#define cubeUV_minTileSize 16.0
	float getFace( vec3 direction ) {
		vec3 absDirection = abs( direction );
		float face = - 1.0;
		if ( absDirection.x > absDirection.z ) {
			if ( absDirection.x > absDirection.y )
				face = direction.x > 0.0 ? 0.0 : 3.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		} else {
			if ( absDirection.z > absDirection.y )
				face = direction.z > 0.0 ? 2.0 : 5.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		}
		return face;
	}
	vec2 getUV( vec3 direction, float face ) {
		vec2 uv;
		if ( face == 0.0 ) {
			uv = vec2( direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 1.0 ) {
			uv = vec2( - direction.x, - direction.z ) / abs( direction.y );
		} else if ( face == 2.0 ) {
			uv = vec2( - direction.x, direction.y ) / abs( direction.z );
		} else if ( face == 3.0 ) {
			uv = vec2( - direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 4.0 ) {
			uv = vec2( - direction.x, direction.z ) / abs( direction.y );
		} else {
			uv = vec2( direction.x, direction.y ) / abs( direction.z );
		}
		return 0.5 * ( uv + 1.0 );
	}
	vec3 bilinearCubeUV( sampler2D envMap, vec3 direction, float mipInt ) {
		float face = getFace( direction );
		float filterInt = max( cubeUV_minMipLevel - mipInt, 0.0 );
		mipInt = max( mipInt, cubeUV_minMipLevel );
		float faceSize = exp2( mipInt );
		highp vec2 uv = getUV( direction, face ) * ( faceSize - 2.0 ) + 1.0;
		if ( face > 2.0 ) {
			uv.y += faceSize;
			face -= 3.0;
		}
		uv.x += face * faceSize;
		uv.x += filterInt * 3.0 * cubeUV_minTileSize;
		uv.y += 4.0 * ( exp2( CUBEUV_MAX_MIP ) - faceSize );
		uv.x *= CUBEUV_TEXEL_WIDTH;
		uv.y *= CUBEUV_TEXEL_HEIGHT;
		#ifdef texture2DGradEXT
			return texture2DGradEXT( envMap, uv, vec2( 0.0 ), vec2( 0.0 ) ).rgb;
		#else
			return texture2D( envMap, uv ).rgb;
		#endif
	}
	#define cubeUV_r0 1.0
	#define cubeUV_m0 - 2.0
	#define cubeUV_r1 0.8
	#define cubeUV_m1 - 1.0
	#define cubeUV_r4 0.4
	#define cubeUV_m4 2.0
	#define cubeUV_r5 0.305
	#define cubeUV_m5 3.0
	#define cubeUV_r6 0.21
	#define cubeUV_m6 4.0
	float roughnessToMip( float roughness ) {
		float mip = 0.0;
		if ( roughness >= cubeUV_r1 ) {
			mip = ( cubeUV_r0 - roughness ) * ( cubeUV_m1 - cubeUV_m0 ) / ( cubeUV_r0 - cubeUV_r1 ) + cubeUV_m0;
		} else if ( roughness >= cubeUV_r4 ) {
			mip = ( cubeUV_r1 - roughness ) * ( cubeUV_m4 - cubeUV_m1 ) / ( cubeUV_r1 - cubeUV_r4 ) + cubeUV_m1;
		} else if ( roughness >= cubeUV_r5 ) {
			mip = ( cubeUV_r4 - roughness ) * ( cubeUV_m5 - cubeUV_m4 ) / ( cubeUV_r4 - cubeUV_r5 ) + cubeUV_m4;
		} else if ( roughness >= cubeUV_r6 ) {
			mip = ( cubeUV_r5 - roughness ) * ( cubeUV_m6 - cubeUV_m5 ) / ( cubeUV_r5 - cubeUV_r6 ) + cubeUV_m5;
		} else {
			mip = - 2.0 * log2( 1.16 * roughness );		}
		return mip;
	}
	vec4 textureCubeUV( sampler2D envMap, vec3 sampleDir, float roughness ) {
		float mip = clamp( roughnessToMip( roughness ), cubeUV_m0, CUBEUV_MAX_MIP );
		float mipF = fract( mip );
		float mipInt = floor( mip );
		vec3 color0 = bilinearCubeUV( envMap, sampleDir, mipInt );
		if ( mipF == 0.0 ) {
			return vec4( color0, 1.0 );
		} else {
			vec3 color1 = bilinearCubeUV( envMap, sampleDir, mipInt + 1.0 );
			return vec4( mix( color0, color1, mipF ), 1.0 );
		}
	}
#endif`,jb=`vec3 transformedNormal = objectNormal;
#ifdef USE_TANGENT
	vec3 transformedTangent = objectTangent;
#endif
#ifdef USE_BATCHING
	mat3 bm = mat3( batchingMatrix );
	transformedNormal /= vec3( dot( bm[ 0 ], bm[ 0 ] ), dot( bm[ 1 ], bm[ 1 ] ), dot( bm[ 2 ], bm[ 2 ] ) );
	transformedNormal = bm * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = bm * transformedTangent;
	#endif
#endif
#ifdef USE_INSTANCING
	mat3 im = mat3( instanceMatrix );
	transformedNormal /= vec3( dot( im[ 0 ], im[ 0 ] ), dot( im[ 1 ], im[ 1 ] ), dot( im[ 2 ], im[ 2 ] ) );
	transformedNormal = im * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = im * transformedTangent;
	#endif
#endif
transformedNormal = normalMatrix * transformedNormal;
#ifdef FLIP_SIDED
	transformedNormal = - transformedNormal;
#endif
#ifdef USE_TANGENT
	transformedTangent = ( modelViewMatrix * vec4( transformedTangent, 0.0 ) ).xyz;
	#ifdef FLIP_SIDED
		transformedTangent = - transformedTangent;
	#endif
#endif`,Kb=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,Zb=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,Jb=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,Qb=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,eS="gl_FragColor = linearToOutputTexel( gl_FragColor );",tS=`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,nS=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vec3 cameraToFrag;
		if ( isOrthographic ) {
			cameraToFrag = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToFrag = normalize( vWorldPosition - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vec3 reflectVec = reflect( cameraToFrag, worldNormal );
		#else
			vec3 reflectVec = refract( cameraToFrag, worldNormal, refractionRatio );
		#endif
	#else
		vec3 reflectVec = vReflect;
	#endif
	#ifdef ENVMAP_TYPE_CUBE
		vec4 envColor = textureCube( envMap, envMapRotation * vec3( flipEnvMap * reflectVec.x, reflectVec.yz ) );
	#else
		vec4 envColor = vec4( 0.0 );
	#endif
	#ifdef ENVMAP_BLENDING_MULTIPLY
		outgoingLight = mix( outgoingLight, outgoingLight * envColor.xyz, specularStrength * reflectivity );
	#elif defined( ENVMAP_BLENDING_MIX )
		outgoingLight = mix( outgoingLight, envColor.xyz, specularStrength * reflectivity );
	#elif defined( ENVMAP_BLENDING_ADD )
		outgoingLight += envColor.xyz * specularStrength * reflectivity;
	#endif
#endif`,iS=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,rS=`#ifdef USE_ENVMAP
	uniform float reflectivity;
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		varying vec3 vWorldPosition;
		uniform float refractionRatio;
	#else
		varying vec3 vReflect;
	#endif
#endif`,sS=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,oS=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vWorldPosition = worldPosition.xyz;
	#else
		vec3 cameraToVertex;
		if ( isOrthographic ) {
			cameraToVertex = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToVertex = normalize( worldPosition.xyz - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vReflect = reflect( cameraToVertex, worldNormal );
		#else
			vReflect = refract( cameraToVertex, worldNormal, refractionRatio );
		#endif
	#endif
#endif`,aS=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,lS=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,cS=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,uS=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,dS=`#ifdef USE_GRADIENTMAP
	uniform sampler2D gradientMap;
#endif
vec3 getGradientIrradiance( vec3 normal, vec3 lightDirection ) {
	float dotNL = dot( normal, lightDirection );
	vec2 coord = vec2( dotNL * 0.5 + 0.5, 0.0 );
	#ifdef USE_GRADIENTMAP
		return vec3( texture2D( gradientMap, coord ).r );
	#else
		vec2 fw = fwidth( coord ) * 0.5;
		return mix( vec3( 0.7 ), vec3( 1.0 ), smoothstep( 0.7 - fw.x, 0.7 + fw.x, coord.x ) );
	#endif
}`,hS=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,fS=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,pS=`varying vec3 vViewPosition;
struct LambertMaterial {
	vec3 diffuseColor;
	float specularStrength;
};
void RE_Direct_Lambert( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Lambert( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Lambert
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,mS=`uniform bool receiveShadow;
uniform vec3 ambientLightColor;
#if defined( USE_LIGHT_PROBES )
	uniform vec3 lightProbe[ 9 ];
#endif
vec3 shGetIrradianceAt( in vec3 normal, in vec3 shCoefficients[ 9 ] ) {
	float x = normal.x, y = normal.y, z = normal.z;
	vec3 result = shCoefficients[ 0 ] * 0.886227;
	result += shCoefficients[ 1 ] * 2.0 * 0.511664 * y;
	result += shCoefficients[ 2 ] * 2.0 * 0.511664 * z;
	result += shCoefficients[ 3 ] * 2.0 * 0.511664 * x;
	result += shCoefficients[ 4 ] * 2.0 * 0.429043 * x * y;
	result += shCoefficients[ 5 ] * 2.0 * 0.429043 * y * z;
	result += shCoefficients[ 6 ] * ( 0.743125 * z * z - 0.247708 );
	result += shCoefficients[ 7 ] * 2.0 * 0.429043 * x * z;
	result += shCoefficients[ 8 ] * 0.429043 * ( x * x - y * y );
	return result;
}
vec3 getLightProbeIrradiance( const in vec3 lightProbe[ 9 ], const in vec3 normal ) {
	vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
	vec3 irradiance = shGetIrradianceAt( worldNormal, lightProbe );
	return irradiance;
}
vec3 getAmbientLightIrradiance( const in vec3 ambientLightColor ) {
	vec3 irradiance = ambientLightColor;
	return irradiance;
}
float getDistanceAttenuation( const in float lightDistance, const in float cutoffDistance, const in float decayExponent ) {
	float distanceFalloff = 1.0 / max( pow( lightDistance, decayExponent ), 0.01 );
	if ( cutoffDistance > 0.0 ) {
		distanceFalloff *= pow2( saturate( 1.0 - pow4( lightDistance / cutoffDistance ) ) );
	}
	return distanceFalloff;
}
float getSpotAttenuation( const in float coneCosine, const in float penumbraCosine, const in float angleCosine ) {
	return smoothstep( coneCosine, penumbraCosine, angleCosine );
}
#if NUM_DIR_LIGHTS > 0
	struct DirectionalLight {
		vec3 direction;
		vec3 color;
	};
	uniform DirectionalLight directionalLights[ NUM_DIR_LIGHTS ];
	void getDirectionalLightInfo( const in DirectionalLight directionalLight, out IncidentLight light ) {
		light.color = directionalLight.color;
		light.direction = directionalLight.direction;
		light.visible = true;
	}
#endif
#if NUM_POINT_LIGHTS > 0
	struct PointLight {
		vec3 position;
		vec3 color;
		float distance;
		float decay;
	};
	uniform PointLight pointLights[ NUM_POINT_LIGHTS ];
	void getPointLightInfo( const in PointLight pointLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = pointLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float lightDistance = length( lVector );
		light.color = pointLight.color;
		light.color *= getDistanceAttenuation( lightDistance, pointLight.distance, pointLight.decay );
		light.visible = ( light.color != vec3( 0.0 ) );
	}
#endif
#if NUM_SPOT_LIGHTS > 0
	struct SpotLight {
		vec3 position;
		vec3 direction;
		vec3 color;
		float distance;
		float decay;
		float coneCos;
		float penumbraCos;
	};
	uniform SpotLight spotLights[ NUM_SPOT_LIGHTS ];
	void getSpotLightInfo( const in SpotLight spotLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = spotLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float angleCos = dot( light.direction, spotLight.direction );
		float spotAttenuation = getSpotAttenuation( spotLight.coneCos, spotLight.penumbraCos, angleCos );
		if ( spotAttenuation > 0.0 ) {
			float lightDistance = length( lVector );
			light.color = spotLight.color * spotAttenuation;
			light.color *= getDistanceAttenuation( lightDistance, spotLight.distance, spotLight.decay );
			light.visible = ( light.color != vec3( 0.0 ) );
		} else {
			light.color = vec3( 0.0 );
			light.visible = false;
		}
	}
#endif
#if NUM_RECT_AREA_LIGHTS > 0
	struct RectAreaLight {
		vec3 color;
		vec3 position;
		vec3 halfWidth;
		vec3 halfHeight;
	};
	uniform sampler2D ltc_1;	uniform sampler2D ltc_2;
	uniform RectAreaLight rectAreaLights[ NUM_RECT_AREA_LIGHTS ];
#endif
#if NUM_HEMI_LIGHTS > 0
	struct HemisphereLight {
		vec3 direction;
		vec3 skyColor;
		vec3 groundColor;
	};
	uniform HemisphereLight hemisphereLights[ NUM_HEMI_LIGHTS ];
	vec3 getHemisphereLightIrradiance( const in HemisphereLight hemiLight, const in vec3 normal ) {
		float dotNL = dot( normal, hemiLight.direction );
		float hemiDiffuseWeight = 0.5 * dotNL + 0.5;
		vec3 irradiance = mix( hemiLight.groundColor, hemiLight.skyColor, hemiDiffuseWeight );
		return irradiance;
	}
#endif`,gS=`#ifdef USE_ENVMAP
	vec3 getIBLIrradiance( const in vec3 normal ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * worldNormal, 1.0 );
			return PI * envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	vec3 getIBLRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 reflectVec = reflect( - viewDir, normal );
			reflectVec = normalize( mix( reflectVec, normal, roughness * roughness) );
			reflectVec = inverseTransformDirection( reflectVec, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * reflectVec, roughness );
			return envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	#ifdef USE_ANISOTROPY
		vec3 getIBLAnisotropyRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness, const in vec3 bitangent, const in float anisotropy ) {
			#ifdef ENVMAP_TYPE_CUBE_UV
				vec3 bentNormal = cross( bitangent, viewDir );
				bentNormal = normalize( cross( bentNormal, bitangent ) );
				bentNormal = normalize( mix( bentNormal, normal, pow2( pow2( 1.0 - anisotropy * ( 1.0 - roughness ) ) ) ) );
				return getIBLRadiance( viewDir, bentNormal, roughness );
			#else
				return vec3( 0.0 );
			#endif
		}
	#endif
#endif`,_S=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,vS=`varying vec3 vViewPosition;
struct ToonMaterial {
	vec3 diffuseColor;
};
void RE_Direct_Toon( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 irradiance = getGradientIrradiance( geometryNormal, directLight.direction ) * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Toon( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Toon
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,xS=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,wS=`varying vec3 vViewPosition;
struct BlinnPhongMaterial {
	vec3 diffuseColor;
	vec3 specularColor;
	float specularShininess;
	float specularStrength;
};
void RE_Direct_BlinnPhong( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
	reflectedLight.directSpecular += irradiance * BRDF_BlinnPhong( directLight.direction, geometryViewDir, geometryNormal, material.specularColor, material.specularShininess ) * material.specularStrength;
}
void RE_IndirectDiffuse_BlinnPhong( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_BlinnPhong
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,yS=`PhysicalMaterial material;
material.diffuseColor = diffuseColor.rgb * ( 1.0 - metalnessFactor );
vec3 dxy = max( abs( dFdx( nonPerturbedNormal ) ), abs( dFdy( nonPerturbedNormal ) ) );
float geometryRoughness = max( max( dxy.x, dxy.y ), dxy.z );
material.roughness = max( roughnessFactor, 0.0525 );material.roughness += geometryRoughness;
material.roughness = min( material.roughness, 1.0 );
#ifdef IOR
	material.ior = ior;
	#ifdef USE_SPECULAR
		float specularIntensityFactor = specularIntensity;
		vec3 specularColorFactor = specularColor;
		#ifdef USE_SPECULAR_COLORMAP
			specularColorFactor *= texture2D( specularColorMap, vSpecularColorMapUv ).rgb;
		#endif
		#ifdef USE_SPECULAR_INTENSITYMAP
			specularIntensityFactor *= texture2D( specularIntensityMap, vSpecularIntensityMapUv ).a;
		#endif
		material.specularF90 = mix( specularIntensityFactor, 1.0, metalnessFactor );
	#else
		float specularIntensityFactor = 1.0;
		vec3 specularColorFactor = vec3( 1.0 );
		material.specularF90 = 1.0;
	#endif
	material.specularColor = mix( min( pow2( ( material.ior - 1.0 ) / ( material.ior + 1.0 ) ) * specularColorFactor, vec3( 1.0 ) ) * specularIntensityFactor, diffuseColor.rgb, metalnessFactor );
#else
	material.specularColor = mix( vec3( 0.04 ), diffuseColor.rgb, metalnessFactor );
	material.specularF90 = 1.0;
#endif
#ifdef USE_CLEARCOAT
	material.clearcoat = clearcoat;
	material.clearcoatRoughness = clearcoatRoughness;
	material.clearcoatF0 = vec3( 0.04 );
	material.clearcoatF90 = 1.0;
	#ifdef USE_CLEARCOATMAP
		material.clearcoat *= texture2D( clearcoatMap, vClearcoatMapUv ).x;
	#endif
	#ifdef USE_CLEARCOAT_ROUGHNESSMAP
		material.clearcoatRoughness *= texture2D( clearcoatRoughnessMap, vClearcoatRoughnessMapUv ).y;
	#endif
	material.clearcoat = saturate( material.clearcoat );	material.clearcoatRoughness = max( material.clearcoatRoughness, 0.0525 );
	material.clearcoatRoughness += geometryRoughness;
	material.clearcoatRoughness = min( material.clearcoatRoughness, 1.0 );
#endif
#ifdef USE_DISPERSION
	material.dispersion = dispersion;
#endif
#ifdef USE_IRIDESCENCE
	material.iridescence = iridescence;
	material.iridescenceIOR = iridescenceIOR;
	#ifdef USE_IRIDESCENCEMAP
		material.iridescence *= texture2D( iridescenceMap, vIridescenceMapUv ).r;
	#endif
	#ifdef USE_IRIDESCENCE_THICKNESSMAP
		material.iridescenceThickness = (iridescenceThicknessMaximum - iridescenceThicknessMinimum) * texture2D( iridescenceThicknessMap, vIridescenceThicknessMapUv ).g + iridescenceThicknessMinimum;
	#else
		material.iridescenceThickness = iridescenceThicknessMaximum;
	#endif
#endif
#ifdef USE_SHEEN
	material.sheenColor = sheenColor;
	#ifdef USE_SHEEN_COLORMAP
		material.sheenColor *= texture2D( sheenColorMap, vSheenColorMapUv ).rgb;
	#endif
	material.sheenRoughness = clamp( sheenRoughness, 0.07, 1.0 );
	#ifdef USE_SHEEN_ROUGHNESSMAP
		material.sheenRoughness *= texture2D( sheenRoughnessMap, vSheenRoughnessMapUv ).a;
	#endif
#endif
#ifdef USE_ANISOTROPY
	#ifdef USE_ANISOTROPYMAP
		mat2 anisotropyMat = mat2( anisotropyVector.x, anisotropyVector.y, - anisotropyVector.y, anisotropyVector.x );
		vec3 anisotropyPolar = texture2D( anisotropyMap, vAnisotropyMapUv ).rgb;
		vec2 anisotropyV = anisotropyMat * normalize( 2.0 * anisotropyPolar.rg - vec2( 1.0 ) ) * anisotropyPolar.b;
	#else
		vec2 anisotropyV = anisotropyVector;
	#endif
	material.anisotropy = length( anisotropyV );
	if( material.anisotropy == 0.0 ) {
		anisotropyV = vec2( 1.0, 0.0 );
	} else {
		anisotropyV /= material.anisotropy;
		material.anisotropy = saturate( material.anisotropy );
	}
	material.alphaT = mix( pow2( material.roughness ), 1.0, pow2( material.anisotropy ) );
	material.anisotropyT = tbn[ 0 ] * anisotropyV.x + tbn[ 1 ] * anisotropyV.y;
	material.anisotropyB = tbn[ 1 ] * anisotropyV.x - tbn[ 0 ] * anisotropyV.y;
#endif`,bS=`struct PhysicalMaterial {
	vec3 diffuseColor;
	float roughness;
	vec3 specularColor;
	float specularF90;
	float dispersion;
	#ifdef USE_CLEARCOAT
		float clearcoat;
		float clearcoatRoughness;
		vec3 clearcoatF0;
		float clearcoatF90;
	#endif
	#ifdef USE_IRIDESCENCE
		float iridescence;
		float iridescenceIOR;
		float iridescenceThickness;
		vec3 iridescenceFresnel;
		vec3 iridescenceF0;
	#endif
	#ifdef USE_SHEEN
		vec3 sheenColor;
		float sheenRoughness;
	#endif
	#ifdef IOR
		float ior;
	#endif
	#ifdef USE_TRANSMISSION
		float transmission;
		float transmissionAlpha;
		float thickness;
		float attenuationDistance;
		vec3 attenuationColor;
	#endif
	#ifdef USE_ANISOTROPY
		float anisotropy;
		float alphaT;
		vec3 anisotropyT;
		vec3 anisotropyB;
	#endif
};
vec3 clearcoatSpecularDirect = vec3( 0.0 );
vec3 clearcoatSpecularIndirect = vec3( 0.0 );
vec3 sheenSpecularDirect = vec3( 0.0 );
vec3 sheenSpecularIndirect = vec3(0.0 );
vec3 Schlick_to_F0( const in vec3 f, const in float f90, const in float dotVH ) {
    float x = clamp( 1.0 - dotVH, 0.0, 1.0 );
    float x2 = x * x;
    float x5 = clamp( x * x2 * x2, 0.0, 0.9999 );
    return ( f - vec3( f90 ) * x5 ) / ( 1.0 - x5 );
}
float V_GGX_SmithCorrelated( const in float alpha, const in float dotNL, const in float dotNV ) {
	float a2 = pow2( alpha );
	float gv = dotNL * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNV ) );
	float gl = dotNV * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNL ) );
	return 0.5 / max( gv + gl, EPSILON );
}
float D_GGX( const in float alpha, const in float dotNH ) {
	float a2 = pow2( alpha );
	float denom = pow2( dotNH ) * ( a2 - 1.0 ) + 1.0;
	return RECIPROCAL_PI * a2 / pow2( denom );
}
#ifdef USE_ANISOTROPY
	float V_GGX_SmithCorrelated_Anisotropic( const in float alphaT, const in float alphaB, const in float dotTV, const in float dotBV, const in float dotTL, const in float dotBL, const in float dotNV, const in float dotNL ) {
		float gv = dotNL * length( vec3( alphaT * dotTV, alphaB * dotBV, dotNV ) );
		float gl = dotNV * length( vec3( alphaT * dotTL, alphaB * dotBL, dotNL ) );
		float v = 0.5 / ( gv + gl );
		return saturate(v);
	}
	float D_GGX_Anisotropic( const in float alphaT, const in float alphaB, const in float dotNH, const in float dotTH, const in float dotBH ) {
		float a2 = alphaT * alphaB;
		highp vec3 v = vec3( alphaB * dotTH, alphaT * dotBH, a2 * dotNH );
		highp float v2 = dot( v, v );
		float w2 = a2 / v2;
		return RECIPROCAL_PI * a2 * pow2 ( w2 );
	}
#endif
#ifdef USE_CLEARCOAT
	vec3 BRDF_GGX_Clearcoat( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material) {
		vec3 f0 = material.clearcoatF0;
		float f90 = material.clearcoatF90;
		float roughness = material.clearcoatRoughness;
		float alpha = pow2( roughness );
		vec3 halfDir = normalize( lightDir + viewDir );
		float dotNL = saturate( dot( normal, lightDir ) );
		float dotNV = saturate( dot( normal, viewDir ) );
		float dotNH = saturate( dot( normal, halfDir ) );
		float dotVH = saturate( dot( viewDir, halfDir ) );
		vec3 F = F_Schlick( f0, f90, dotVH );
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
		return F * ( V * D );
	}
#endif
vec3 BRDF_GGX( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 f0 = material.specularColor;
	float f90 = material.specularF90;
	float roughness = material.roughness;
	float alpha = pow2( roughness );
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( f0, f90, dotVH );
	#ifdef USE_IRIDESCENCE
		F = mix( F, material.iridescenceFresnel, material.iridescence );
	#endif
	#ifdef USE_ANISOTROPY
		float dotTL = dot( material.anisotropyT, lightDir );
		float dotTV = dot( material.anisotropyT, viewDir );
		float dotTH = dot( material.anisotropyT, halfDir );
		float dotBL = dot( material.anisotropyB, lightDir );
		float dotBV = dot( material.anisotropyB, viewDir );
		float dotBH = dot( material.anisotropyB, halfDir );
		float V = V_GGX_SmithCorrelated_Anisotropic( material.alphaT, alpha, dotTV, dotBV, dotTL, dotBL, dotNV, dotNL );
		float D = D_GGX_Anisotropic( material.alphaT, alpha, dotNH, dotTH, dotBH );
	#else
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
	#endif
	return F * ( V * D );
}
vec2 LTC_Uv( const in vec3 N, const in vec3 V, const in float roughness ) {
	const float LUT_SIZE = 64.0;
	const float LUT_SCALE = ( LUT_SIZE - 1.0 ) / LUT_SIZE;
	const float LUT_BIAS = 0.5 / LUT_SIZE;
	float dotNV = saturate( dot( N, V ) );
	vec2 uv = vec2( roughness, sqrt( 1.0 - dotNV ) );
	uv = uv * LUT_SCALE + LUT_BIAS;
	return uv;
}
float LTC_ClippedSphereFormFactor( const in vec3 f ) {
	float l = length( f );
	return max( ( l * l + f.z ) / ( l + 1.0 ), 0.0 );
}
vec3 LTC_EdgeVectorFormFactor( const in vec3 v1, const in vec3 v2 ) {
	float x = dot( v1, v2 );
	float y = abs( x );
	float a = 0.8543985 + ( 0.4965155 + 0.0145206 * y ) * y;
	float b = 3.4175940 + ( 4.1616724 + y ) * y;
	float v = a / b;
	float theta_sintheta = ( x > 0.0 ) ? v : 0.5 * inversesqrt( max( 1.0 - x * x, 1e-7 ) ) - v;
	return cross( v1, v2 ) * theta_sintheta;
}
vec3 LTC_Evaluate( const in vec3 N, const in vec3 V, const in vec3 P, const in mat3 mInv, const in vec3 rectCoords[ 4 ] ) {
	vec3 v1 = rectCoords[ 1 ] - rectCoords[ 0 ];
	vec3 v2 = rectCoords[ 3 ] - rectCoords[ 0 ];
	vec3 lightNormal = cross( v1, v2 );
	if( dot( lightNormal, P - rectCoords[ 0 ] ) < 0.0 ) return vec3( 0.0 );
	vec3 T1, T2;
	T1 = normalize( V - N * dot( V, N ) );
	T2 = - cross( N, T1 );
	mat3 mat = mInv * transposeMat3( mat3( T1, T2, N ) );
	vec3 coords[ 4 ];
	coords[ 0 ] = mat * ( rectCoords[ 0 ] - P );
	coords[ 1 ] = mat * ( rectCoords[ 1 ] - P );
	coords[ 2 ] = mat * ( rectCoords[ 2 ] - P );
	coords[ 3 ] = mat * ( rectCoords[ 3 ] - P );
	coords[ 0 ] = normalize( coords[ 0 ] );
	coords[ 1 ] = normalize( coords[ 1 ] );
	coords[ 2 ] = normalize( coords[ 2 ] );
	coords[ 3 ] = normalize( coords[ 3 ] );
	vec3 vectorFormFactor = vec3( 0.0 );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 0 ], coords[ 1 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 1 ], coords[ 2 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 2 ], coords[ 3 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 3 ], coords[ 0 ] );
	float result = LTC_ClippedSphereFormFactor( vectorFormFactor );
	return vec3( result );
}
#if defined( USE_SHEEN )
float D_Charlie( float roughness, float dotNH ) {
	float alpha = pow2( roughness );
	float invAlpha = 1.0 / alpha;
	float cos2h = dotNH * dotNH;
	float sin2h = max( 1.0 - cos2h, 0.0078125 );
	return ( 2.0 + invAlpha ) * pow( sin2h, invAlpha * 0.5 ) / ( 2.0 * PI );
}
float V_Neubelt( float dotNV, float dotNL ) {
	return saturate( 1.0 / ( 4.0 * ( dotNL + dotNV - dotNL * dotNV ) ) );
}
vec3 BRDF_Sheen( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, vec3 sheenColor, const in float sheenRoughness ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float D = D_Charlie( sheenRoughness, dotNH );
	float V = V_Neubelt( dotNV, dotNL );
	return sheenColor * ( D * V );
}
#endif
float IBLSheenBRDF( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	float r2 = roughness * roughness;
	float a = roughness < 0.25 ? -339.2 * r2 + 161.4 * roughness - 25.9 : -8.48 * r2 + 14.3 * roughness - 9.95;
	float b = roughness < 0.25 ? 44.0 * r2 - 23.7 * roughness + 3.26 : 1.97 * r2 - 3.27 * roughness + 0.72;
	float DG = exp( a * dotNV + b ) + ( roughness < 0.25 ? 0.0 : 0.1 * ( roughness - 0.25 ) );
	return saturate( DG * RECIPROCAL_PI );
}
vec2 DFGApprox( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	const vec4 c0 = vec4( - 1, - 0.0275, - 0.572, 0.022 );
	const vec4 c1 = vec4( 1, 0.0425, 1.04, - 0.04 );
	vec4 r = roughness * c0 + c1;
	float a004 = min( r.x * r.x, exp2( - 9.28 * dotNV ) ) * r.x + r.y;
	vec2 fab = vec2( - 1.04, 1.04 ) * a004 + r.zw;
	return fab;
}
vec3 EnvironmentBRDF( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness ) {
	vec2 fab = DFGApprox( normal, viewDir, roughness );
	return specularColor * fab.x + specularF90 * fab.y;
}
#ifdef USE_IRIDESCENCE
void computeMultiscatteringIridescence( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float iridescence, const in vec3 iridescenceF0, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#else
void computeMultiscattering( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#endif
	vec2 fab = DFGApprox( normal, viewDir, roughness );
	#ifdef USE_IRIDESCENCE
		vec3 Fr = mix( specularColor, iridescenceF0, iridescence );
	#else
		vec3 Fr = specularColor;
	#endif
	vec3 FssEss = Fr * fab.x + specularF90 * fab.y;
	float Ess = fab.x + fab.y;
	float Ems = 1.0 - Ess;
	vec3 Favg = Fr + ( 1.0 - Fr ) * 0.047619;	vec3 Fms = FssEss * Favg / ( 1.0 - Ems * Favg );
	singleScatter += FssEss;
	multiScatter += Fms * Ems;
}
#if NUM_RECT_AREA_LIGHTS > 0
	void RE_Direct_RectArea_Physical( const in RectAreaLight rectAreaLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
		vec3 normal = geometryNormal;
		vec3 viewDir = geometryViewDir;
		vec3 position = geometryPosition;
		vec3 lightPos = rectAreaLight.position;
		vec3 halfWidth = rectAreaLight.halfWidth;
		vec3 halfHeight = rectAreaLight.halfHeight;
		vec3 lightColor = rectAreaLight.color;
		float roughness = material.roughness;
		vec3 rectCoords[ 4 ];
		rectCoords[ 0 ] = lightPos + halfWidth - halfHeight;		rectCoords[ 1 ] = lightPos - halfWidth - halfHeight;
		rectCoords[ 2 ] = lightPos - halfWidth + halfHeight;
		rectCoords[ 3 ] = lightPos + halfWidth + halfHeight;
		vec2 uv = LTC_Uv( normal, viewDir, roughness );
		vec4 t1 = texture2D( ltc_1, uv );
		vec4 t2 = texture2D( ltc_2, uv );
		mat3 mInv = mat3(
			vec3( t1.x, 0, t1.y ),
			vec3(    0, 1,    0 ),
			vec3( t1.z, 0, t1.w )
		);
		vec3 fresnel = ( material.specularColor * t2.x + ( vec3( 1.0 ) - material.specularColor ) * t2.y );
		reflectedLight.directSpecular += lightColor * fresnel * LTC_Evaluate( normal, viewDir, position, mInv, rectCoords );
		reflectedLight.directDiffuse += lightColor * material.diffuseColor * LTC_Evaluate( normal, viewDir, position, mat3( 1.0 ), rectCoords );
	}
#endif
void RE_Direct_Physical( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	#ifdef USE_CLEARCOAT
		float dotNLcc = saturate( dot( geometryClearcoatNormal, directLight.direction ) );
		vec3 ccIrradiance = dotNLcc * directLight.color;
		clearcoatSpecularDirect += ccIrradiance * BRDF_GGX_Clearcoat( directLight.direction, geometryViewDir, geometryClearcoatNormal, material );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularDirect += irradiance * BRDF_Sheen( directLight.direction, geometryViewDir, geometryNormal, material.sheenColor, material.sheenRoughness );
	#endif
	reflectedLight.directSpecular += irradiance * BRDF_GGX( directLight.direction, geometryViewDir, geometryNormal, material );
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Physical( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectSpecular_Physical( const in vec3 radiance, const in vec3 irradiance, const in vec3 clearcoatRadiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight) {
	#ifdef USE_CLEARCOAT
		clearcoatSpecularIndirect += clearcoatRadiance * EnvironmentBRDF( geometryClearcoatNormal, geometryViewDir, material.clearcoatF0, material.clearcoatF90, material.clearcoatRoughness );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularIndirect += irradiance * material.sheenColor * IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
	#endif
	vec3 singleScattering = vec3( 0.0 );
	vec3 multiScattering = vec3( 0.0 );
	vec3 cosineWeightedIrradiance = irradiance * RECIPROCAL_PI;
	#ifdef USE_IRIDESCENCE
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.iridescence, material.iridescenceFresnel, material.roughness, singleScattering, multiScattering );
	#else
		computeMultiscattering( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.roughness, singleScattering, multiScattering );
	#endif
	vec3 totalScattering = singleScattering + multiScattering;
	vec3 diffuse = material.diffuseColor * ( 1.0 - max( max( totalScattering.r, totalScattering.g ), totalScattering.b ) );
	reflectedLight.indirectSpecular += radiance * singleScattering;
	reflectedLight.indirectSpecular += multiScattering * cosineWeightedIrradiance;
	reflectedLight.indirectDiffuse += diffuse * cosineWeightedIrradiance;
}
#define RE_Direct				RE_Direct_Physical
#define RE_Direct_RectArea		RE_Direct_RectArea_Physical
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Physical
#define RE_IndirectSpecular		RE_IndirectSpecular_Physical
float computeSpecularOcclusion( const in float dotNV, const in float ambientOcclusion, const in float roughness ) {
	return saturate( pow( dotNV + ambientOcclusion, exp2( - 16.0 * roughness - 1.0 ) ) - 1.0 + ambientOcclusion );
}`,SS=`
vec3 geometryPosition = - vViewPosition;
vec3 geometryNormal = normal;
vec3 geometryViewDir = ( isOrthographic ) ? vec3( 0, 0, 1 ) : normalize( vViewPosition );
vec3 geometryClearcoatNormal = vec3( 0.0 );
#ifdef USE_CLEARCOAT
	geometryClearcoatNormal = clearcoatNormal;
#endif
#ifdef USE_IRIDESCENCE
	float dotNVi = saturate( dot( normal, geometryViewDir ) );
	if ( material.iridescenceThickness == 0.0 ) {
		material.iridescence = 0.0;
	} else {
		material.iridescence = saturate( material.iridescence );
	}
	if ( material.iridescence > 0.0 ) {
		material.iridescenceFresnel = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.specularColor );
		material.iridescenceF0 = Schlick_to_F0( material.iridescenceFresnel, 1.0, dotNVi );
	}
#endif
IncidentLight directLight;
#if ( NUM_POINT_LIGHTS > 0 ) && defined( RE_Direct )
	PointLight pointLight;
	#if defined( USE_SHADOWMAP ) && NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHTS; i ++ ) {
		pointLight = pointLights[ i ];
		getPointLightInfo( pointLight, geometryPosition, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_POINT_LIGHT_SHADOWS )
		pointLightShadow = pointLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getPointShadow( pointShadowMap[ i ], pointLightShadow.shadowMapSize, pointLightShadow.shadowIntensity, pointLightShadow.shadowBias, pointLightShadow.shadowRadius, vPointShadowCoord[ i ], pointLightShadow.shadowCameraNear, pointLightShadow.shadowCameraFar ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_SPOT_LIGHTS > 0 ) && defined( RE_Direct )
	SpotLight spotLight;
	vec4 spotColor;
	vec3 spotLightCoord;
	bool inSpotLightMap;
	#if defined( USE_SHADOWMAP ) && NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHTS; i ++ ) {
		spotLight = spotLights[ i ];
		getSpotLightInfo( spotLight, geometryPosition, directLight );
		#if ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#define SPOT_LIGHT_MAP_INDEX UNROLLED_LOOP_INDEX
		#elif ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		#define SPOT_LIGHT_MAP_INDEX NUM_SPOT_LIGHT_MAPS
		#else
		#define SPOT_LIGHT_MAP_INDEX ( UNROLLED_LOOP_INDEX - NUM_SPOT_LIGHT_SHADOWS + NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#endif
		#if ( SPOT_LIGHT_MAP_INDEX < NUM_SPOT_LIGHT_MAPS )
			spotLightCoord = vSpotLightCoord[ i ].xyz / vSpotLightCoord[ i ].w;
			inSpotLightMap = all( lessThan( abs( spotLightCoord * 2. - 1. ), vec3( 1.0 ) ) );
			spotColor = texture2D( spotLightMap[ SPOT_LIGHT_MAP_INDEX ], spotLightCoord.xy );
			directLight.color = inSpotLightMap ? directLight.color * spotColor.rgb : directLight.color;
		#endif
		#undef SPOT_LIGHT_MAP_INDEX
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		spotLightShadow = spotLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( spotShadowMap[ i ], spotLightShadow.shadowMapSize, spotLightShadow.shadowIntensity, spotLightShadow.shadowBias, spotLightShadow.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_DIR_LIGHTS > 0 ) && defined( RE_Direct )
	DirectionalLight directionalLight;
	#if defined( USE_SHADOWMAP ) && NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHTS; i ++ ) {
		directionalLight = directionalLights[ i ];
		getDirectionalLightInfo( directionalLight, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_DIR_LIGHT_SHADOWS )
		directionalLightShadow = directionalLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( directionalShadowMap[ i ], directionalLightShadow.shadowMapSize, directionalLightShadow.shadowIntensity, directionalLightShadow.shadowBias, directionalLightShadow.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_RECT_AREA_LIGHTS > 0 ) && defined( RE_Direct_RectArea )
	RectAreaLight rectAreaLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_RECT_AREA_LIGHTS; i ++ ) {
		rectAreaLight = rectAreaLights[ i ];
		RE_Direct_RectArea( rectAreaLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if defined( RE_IndirectDiffuse )
	vec3 iblIrradiance = vec3( 0.0 );
	vec3 irradiance = getAmbientLightIrradiance( ambientLightColor );
	#if defined( USE_LIGHT_PROBES )
		irradiance += getLightProbeIrradiance( lightProbe, geometryNormal );
	#endif
	#if ( NUM_HEMI_LIGHTS > 0 )
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_HEMI_LIGHTS; i ++ ) {
			irradiance += getHemisphereLightIrradiance( hemisphereLights[ i ], geometryNormal );
		}
		#pragma unroll_loop_end
	#endif
#endif
#if defined( RE_IndirectSpecular )
	vec3 radiance = vec3( 0.0 );
	vec3 clearcoatRadiance = vec3( 0.0 );
#endif`,ES=`#if defined( RE_IndirectDiffuse )
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;
		irradiance += lightMapIrradiance;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD ) && defined( ENVMAP_TYPE_CUBE_UV )
		iblIrradiance += getIBLIrradiance( geometryNormal );
	#endif
#endif
#if defined( USE_ENVMAP ) && defined( RE_IndirectSpecular )
	#ifdef USE_ANISOTROPY
		radiance += getIBLAnisotropyRadiance( geometryViewDir, geometryNormal, material.roughness, material.anisotropyB, material.anisotropy );
	#else
		radiance += getIBLRadiance( geometryViewDir, geometryNormal, material.roughness );
	#endif
	#ifdef USE_CLEARCOAT
		clearcoatRadiance += getIBLRadiance( geometryViewDir, geometryClearcoatNormal, material.clearcoatRoughness );
	#endif
#endif`,MS=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,TS=`#if defined( USE_LOGARITHMIC_DEPTH_BUFFER )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,AS=`#if defined( USE_LOGARITHMIC_DEPTH_BUFFER )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,CS=`#ifdef USE_LOGARITHMIC_DEPTH_BUFFER
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,PS=`#ifdef USE_LOGARITHMIC_DEPTH_BUFFER
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,RS=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,DS=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,LS=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
	#if defined( USE_POINTS_UV )
		vec2 uv = vUv;
	#else
		vec2 uv = ( uvTransform * vec3( gl_PointCoord.x, 1.0 - gl_PointCoord.y, 1 ) ).xy;
	#endif
#endif
#ifdef USE_MAP
	diffuseColor *= texture2D( map, uv );
#endif
#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, uv ).g;
#endif`,IS=`#if defined( USE_POINTS_UV )
	varying vec2 vUv;
#else
	#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
		uniform mat3 uvTransform;
	#endif
#endif
#ifdef USE_MAP
	uniform sampler2D map;
#endif
#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,US=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,OS=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,FS=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,NS=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,kS=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,BS=`#ifdef USE_MORPHTARGETS
	#ifndef USE_INSTANCING_MORPH
		uniform float morphTargetBaseInfluence;
		uniform float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	#endif
	uniform sampler2DArray morphTargetsTexture;
	uniform ivec2 morphTargetsTextureSize;
	vec4 getMorph( const in int vertexIndex, const in int morphTargetIndex, const in int offset ) {
		int texelIndex = vertexIndex * MORPHTARGETS_TEXTURE_STRIDE + offset;
		int y = texelIndex / morphTargetsTextureSize.x;
		int x = texelIndex - y * morphTargetsTextureSize.x;
		ivec3 morphUV = ivec3( x, y, morphTargetIndex );
		return texelFetch( morphTargetsTexture, morphUV, 0 );
	}
#endif`,zS=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,VS=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
#ifdef FLAT_SHADED
	vec3 fdx = dFdx( vViewPosition );
	vec3 fdy = dFdy( vViewPosition );
	vec3 normal = normalize( cross( fdx, fdy ) );
#else
	vec3 normal = normalize( vNormal );
	#ifdef DOUBLE_SIDED
		normal *= faceDirection;
	#endif
#endif
#if defined( USE_NORMALMAP_TANGENTSPACE ) || defined( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY )
	#ifdef USE_TANGENT
		mat3 tbn = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn = getTangentFrame( - vViewPosition, normal,
		#if defined( USE_NORMALMAP )
			vNormalMapUv
		#elif defined( USE_CLEARCOAT_NORMALMAP )
			vClearcoatNormalMapUv
		#else
			vUv
		#endif
		);
	#endif
	#if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
		tbn[0] *= faceDirection;
		tbn[1] *= faceDirection;
	#endif
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	#ifdef USE_TANGENT
		mat3 tbn2 = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn2 = getTangentFrame( - vViewPosition, normal, vClearcoatNormalMapUv );
	#endif
	#if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
		tbn2[0] *= faceDirection;
		tbn2[1] *= faceDirection;
	#endif
#endif
vec3 nonPerturbedNormal = normal;`,HS=`#ifdef USE_NORMALMAP_OBJECTSPACE
	normal = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	#ifdef FLIP_SIDED
		normal = - normal;
	#endif
	#ifdef DOUBLE_SIDED
		normal = normal * faceDirection;
	#endif
	normal = normalize( normalMatrix * normal );
#elif defined( USE_NORMALMAP_TANGENTSPACE )
	vec3 mapN = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	mapN.xy *= normalScale;
	normal = normalize( tbn * mapN );
#elif defined( USE_BUMPMAP )
	normal = perturbNormalArb( - vViewPosition, normal, dHdxy_fwd(), faceDirection );
#endif`,GS=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,WS=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,XS=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,$S=`#ifdef USE_NORMALMAP
	uniform sampler2D normalMap;
	uniform vec2 normalScale;
#endif
#ifdef USE_NORMALMAP_OBJECTSPACE
	uniform mat3 normalMatrix;
#endif
#if ! defined ( USE_TANGENT ) && ( defined ( USE_NORMALMAP_TANGENTSPACE ) || defined ( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY ) )
	mat3 getTangentFrame( vec3 eye_pos, vec3 surf_norm, vec2 uv ) {
		vec3 q0 = dFdx( eye_pos.xyz );
		vec3 q1 = dFdy( eye_pos.xyz );
		vec2 st0 = dFdx( uv.st );
		vec2 st1 = dFdy( uv.st );
		vec3 N = surf_norm;
		vec3 q1perp = cross( q1, N );
		vec3 q0perp = cross( N, q0 );
		vec3 T = q1perp * st0.x + q0perp * st1.x;
		vec3 B = q1perp * st0.y + q0perp * st1.y;
		float det = max( dot( T, T ), dot( B, B ) );
		float scale = ( det == 0.0 ) ? 0.0 : inversesqrt( det );
		return mat3( T * scale, B * scale, N );
	}
#endif`,qS=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,YS=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,jS=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,KS=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,ZS=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,JS=`vec3 packNormalToRGB( const in vec3 normal ) {
	return normalize( normal ) * 0.5 + 0.5;
}
vec3 unpackRGBToNormal( const in vec3 rgb ) {
	return 2.0 * rgb.xyz - 1.0;
}
const float PackUpscale = 256. / 255.;const float UnpackDownscale = 255. / 256.;const float ShiftRight8 = 1. / 256.;
const float Inv255 = 1. / 255.;
const vec4 PackFactors = vec4( 1.0, 256.0, 256.0 * 256.0, 256.0 * 256.0 * 256.0 );
const vec2 UnpackFactors2 = vec2( UnpackDownscale, 1.0 / PackFactors.g );
const vec3 UnpackFactors3 = vec3( UnpackDownscale / PackFactors.rg, 1.0 / PackFactors.b );
const vec4 UnpackFactors4 = vec4( UnpackDownscale / PackFactors.rgb, 1.0 / PackFactors.a );
vec4 packDepthToRGBA( const in float v ) {
	if( v <= 0.0 )
		return vec4( 0., 0., 0., 0. );
	if( v >= 1.0 )
		return vec4( 1., 1., 1., 1. );
	float vuf;
	float af = modf( v * PackFactors.a, vuf );
	float bf = modf( vuf * ShiftRight8, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec4( vuf * Inv255, gf * PackUpscale, bf * PackUpscale, af );
}
vec3 packDepthToRGB( const in float v ) {
	if( v <= 0.0 )
		return vec3( 0., 0., 0. );
	if( v >= 1.0 )
		return vec3( 1., 1., 1. );
	float vuf;
	float bf = modf( v * PackFactors.b, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec3( vuf * Inv255, gf * PackUpscale, bf );
}
vec2 packDepthToRG( const in float v ) {
	if( v <= 0.0 )
		return vec2( 0., 0. );
	if( v >= 1.0 )
		return vec2( 1., 1. );
	float vuf;
	float gf = modf( v * 256., vuf );
	return vec2( vuf * Inv255, gf );
}
float unpackRGBAToDepth( const in vec4 v ) {
	return dot( v, UnpackFactors4 );
}
float unpackRGBToDepth( const in vec3 v ) {
	return dot( v, UnpackFactors3 );
}
float unpackRGToDepth( const in vec2 v ) {
	return v.r * UnpackFactors2.r + v.g * UnpackFactors2.g;
}
vec4 pack2HalfToRGBA( const in vec2 v ) {
	vec4 r = vec4( v.x, fract( v.x * 255.0 ), v.y, fract( v.y * 255.0 ) );
	return vec4( r.x - r.y / 255.0, r.y, r.z - r.w / 255.0, r.w );
}
vec2 unpackRGBATo2Half( const in vec4 v ) {
	return vec2( v.x + ( v.y / 255.0 ), v.z + ( v.w / 255.0 ) );
}
float viewZToOrthographicDepth( const in float viewZ, const in float near, const in float far ) {
	return ( viewZ + near ) / ( near - far );
}
float orthographicDepthToViewZ( const in float depth, const in float near, const in float far ) {
	return depth * ( near - far ) - near;
}
float viewZToPerspectiveDepth( const in float viewZ, const in float near, const in float far ) {
	return ( ( near + viewZ ) * far ) / ( ( far - near ) * viewZ );
}
float perspectiveDepthToViewZ( const in float depth, const in float near, const in float far ) {
	return ( near * far ) / ( ( far - near ) * depth - far );
}`,QS=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,eE=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,tE=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,nE=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,iE=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,rE=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,sE=`#if NUM_SPOT_LIGHT_COORDS > 0
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#if NUM_SPOT_LIGHT_MAPS > 0
	uniform sampler2D spotLightMap[ NUM_SPOT_LIGHT_MAPS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform sampler2D directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		uniform sampler2D spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform sampler2D pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
	float texture2DCompare( sampler2D depths, vec2 uv, float compare ) {
		float depth = unpackRGBAToDepth( texture2D( depths, uv ) );
		#ifdef USE_REVERSED_DEPTH_BUFFER
			return step( depth, compare );
		#else
			return step( compare, depth );
		#endif
	}
	vec2 texture2DDistribution( sampler2D shadow, vec2 uv ) {
		return unpackRGBATo2Half( texture2D( shadow, uv ) );
	}
	float VSMShadow( sampler2D shadow, vec2 uv, float compare ) {
		float occlusion = 1.0;
		vec2 distribution = texture2DDistribution( shadow, uv );
		#ifdef USE_REVERSED_DEPTH_BUFFER
			float hard_shadow = step( distribution.x, compare );
		#else
			float hard_shadow = step( compare, distribution.x );
		#endif
		if ( hard_shadow != 1.0 ) {
			float distance = compare - distribution.x;
			float variance = max( 0.00000, distribution.y * distribution.y );
			float softness_probability = variance / (variance + distance * distance );			softness_probability = clamp( ( softness_probability - 0.3 ) / ( 0.95 - 0.3 ), 0.0, 1.0 );			occlusion = clamp( max( hard_shadow, softness_probability ), 0.0, 1.0 );
		}
		return occlusion;
	}
	float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
		float shadow = 1.0;
		shadowCoord.xyz /= shadowCoord.w;
		shadowCoord.z += shadowBias;
		bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
		bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
		if ( frustumTest ) {
		#if defined( SHADOWMAP_TYPE_PCF )
			vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
			float dx0 = - texelSize.x * shadowRadius;
			float dy0 = - texelSize.y * shadowRadius;
			float dx1 = + texelSize.x * shadowRadius;
			float dy1 = + texelSize.y * shadowRadius;
			float dx2 = dx0 / 2.0;
			float dy2 = dy0 / 2.0;
			float dx3 = dx1 / 2.0;
			float dy3 = dy1 / 2.0;
			shadow = (
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy, shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, dy1 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy1 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, dy1 ), shadowCoord.z )
			) * ( 1.0 / 17.0 );
		#elif defined( SHADOWMAP_TYPE_PCF_SOFT )
			vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
			float dx = texelSize.x;
			float dy = texelSize.y;
			vec2 uv = shadowCoord.xy;
			vec2 f = fract( uv * shadowMapSize + 0.5 );
			uv -= f * texelSize;
			shadow = (
				texture2DCompare( shadowMap, uv, shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + vec2( dx, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + vec2( 0.0, dy ), shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + texelSize, shadowCoord.z ) +
				mix( texture2DCompare( shadowMap, uv + vec2( -dx, 0.0 ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, 0.0 ), shadowCoord.z ),
					 f.x ) +
				mix( texture2DCompare( shadowMap, uv + vec2( -dx, dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, dy ), shadowCoord.z ),
					 f.x ) +
				mix( texture2DCompare( shadowMap, uv + vec2( 0.0, -dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 0.0, 2.0 * dy ), shadowCoord.z ),
					 f.y ) +
				mix( texture2DCompare( shadowMap, uv + vec2( dx, -dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( dx, 2.0 * dy ), shadowCoord.z ),
					 f.y ) +
				mix( mix( texture2DCompare( shadowMap, uv + vec2( -dx, -dy ), shadowCoord.z ),
						  texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, -dy ), shadowCoord.z ),
						  f.x ),
					 mix( texture2DCompare( shadowMap, uv + vec2( -dx, 2.0 * dy ), shadowCoord.z ),
						  texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, 2.0 * dy ), shadowCoord.z ),
						  f.x ),
					 f.y )
			) * ( 1.0 / 9.0 );
		#elif defined( SHADOWMAP_TYPE_VSM )
			shadow = VSMShadow( shadowMap, shadowCoord.xy, shadowCoord.z );
		#else
			shadow = texture2DCompare( shadowMap, shadowCoord.xy, shadowCoord.z );
		#endif
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
	vec2 cubeToUV( vec3 v, float texelSizeY ) {
		vec3 absV = abs( v );
		float scaleToCube = 1.0 / max( absV.x, max( absV.y, absV.z ) );
		absV *= scaleToCube;
		v *= scaleToCube * ( 1.0 - 2.0 * texelSizeY );
		vec2 planar = v.xy;
		float almostATexel = 1.5 * texelSizeY;
		float almostOne = 1.0 - almostATexel;
		if ( absV.z >= almostOne ) {
			if ( v.z > 0.0 )
				planar.x = 4.0 - v.x;
		} else if ( absV.x >= almostOne ) {
			float signX = sign( v.x );
			planar.x = v.z * signX + 2.0 * signX;
		} else if ( absV.y >= almostOne ) {
			float signY = sign( v.y );
			planar.x = v.x + 2.0 * signY + 2.0;
			planar.y = v.z * signY - 2.0;
		}
		return vec2( 0.125, 0.25 ) * planar + vec2( 0.375, 0.75 );
	}
	float getPointShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		float shadow = 1.0;
		vec3 lightToPosition = shadowCoord.xyz;
		
		float lightToPositionLength = length( lightToPosition );
		if ( lightToPositionLength - shadowCameraFar <= 0.0 && lightToPositionLength - shadowCameraNear >= 0.0 ) {
			float dp = ( lightToPositionLength - shadowCameraNear ) / ( shadowCameraFar - shadowCameraNear );			dp += shadowBias;
			vec3 bd3D = normalize( lightToPosition );
			vec2 texelSize = vec2( 1.0 ) / ( shadowMapSize * vec2( 4.0, 2.0 ) );
			#if defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_PCF_SOFT ) || defined( SHADOWMAP_TYPE_VSM )
				vec2 offset = vec2( - 1, 1 ) * shadowRadius * texelSize.y;
				shadow = (
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xyy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yyy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xyx, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yyx, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xxy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yxy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xxx, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yxx, texelSize.y ), dp )
				) * ( 1.0 / 9.0 );
			#else
				shadow = texture2DCompare( shadowMap, cubeToUV( bd3D, texelSize.y ), dp );
			#endif
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
#endif`,oE=`#if NUM_SPOT_LIGHT_COORDS > 0
	uniform mat4 spotLightMatrix[ NUM_SPOT_LIGHT_COORDS ];
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform mat4 directionalShadowMatrix[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform mat4 pointShadowMatrix[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
#endif`,aE=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
	vec3 shadowWorldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
	vec4 shadowWorldPosition;
#endif
#if defined( USE_SHADOWMAP )
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * directionalLightShadows[ i ].shadowNormalBias, 0 );
			vDirectionalShadowCoord[ i ] = directionalShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * pointLightShadows[ i ].shadowNormalBias, 0 );
			vPointShadowCoord[ i ] = pointShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
#endif
#if NUM_SPOT_LIGHT_COORDS > 0
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_COORDS; i ++ ) {
		shadowWorldPosition = worldPosition;
		#if ( defined( USE_SHADOWMAP ) && UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
			shadowWorldPosition.xyz += shadowWorldNormal * spotLightShadows[ i ].shadowNormalBias;
		#endif
		vSpotLightCoord[ i ] = spotLightMatrix[ i ] * shadowWorldPosition;
	}
	#pragma unroll_loop_end
#endif`,lE=`float getShadowMask() {
	float shadow = 1.0;
	#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
		directionalLight = directionalLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( directionalShadowMap[ i ], directionalLight.shadowMapSize, directionalLight.shadowIntensity, directionalLight.shadowBias, directionalLight.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_SHADOWS; i ++ ) {
		spotLight = spotLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( spotShadowMap[ i ], spotLight.shadowMapSize, spotLight.shadowIntensity, spotLight.shadowBias, spotLight.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
		pointLight = pointLightShadows[ i ];
		shadow *= receiveShadow ? getPointShadow( pointShadowMap[ i ], pointLight.shadowMapSize, pointLight.shadowIntensity, pointLight.shadowBias, pointLight.shadowRadius, vPointShadowCoord[ i ], pointLight.shadowCameraNear, pointLight.shadowCameraFar ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#endif
	return shadow;
}`,cE=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,uE=`#ifdef USE_SKINNING
	uniform mat4 bindMatrix;
	uniform mat4 bindMatrixInverse;
	uniform highp sampler2D boneTexture;
	mat4 getBoneMatrix( const in float i ) {
		int size = textureSize( boneTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( boneTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( boneTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( boneTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( boneTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
#endif`,dE=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,hE=`#ifdef USE_SKINNING
	mat4 skinMatrix = mat4( 0.0 );
	skinMatrix += skinWeight.x * boneMatX;
	skinMatrix += skinWeight.y * boneMatY;
	skinMatrix += skinWeight.z * boneMatZ;
	skinMatrix += skinWeight.w * boneMatW;
	skinMatrix = bindMatrixInverse * skinMatrix * bindMatrix;
	objectNormal = vec4( skinMatrix * vec4( objectNormal, 0.0 ) ).xyz;
	#ifdef USE_TANGENT
		objectTangent = vec4( skinMatrix * vec4( objectTangent, 0.0 ) ).xyz;
	#endif
#endif`,fE=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,pE=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,mE=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,gE=`#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
uniform float toneMappingExposure;
vec3 LinearToneMapping( vec3 color ) {
	return saturate( toneMappingExposure * color );
}
vec3 ReinhardToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	return saturate( color / ( vec3( 1.0 ) + color ) );
}
vec3 CineonToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	color = max( vec3( 0.0 ), color - 0.004 );
	return pow( ( color * ( 6.2 * color + 0.5 ) ) / ( color * ( 6.2 * color + 1.7 ) + 0.06 ), vec3( 2.2 ) );
}
vec3 RRTAndODTFit( vec3 v ) {
	vec3 a = v * ( v + 0.0245786 ) - 0.000090537;
	vec3 b = v * ( 0.983729 * v + 0.4329510 ) + 0.238081;
	return a / b;
}
vec3 ACESFilmicToneMapping( vec3 color ) {
	const mat3 ACESInputMat = mat3(
		vec3( 0.59719, 0.07600, 0.02840 ),		vec3( 0.35458, 0.90834, 0.13383 ),
		vec3( 0.04823, 0.01566, 0.83777 )
	);
	const mat3 ACESOutputMat = mat3(
		vec3(  1.60475, -0.10208, -0.00327 ),		vec3( -0.53108,  1.10813, -0.07276 ),
		vec3( -0.07367, -0.00605,  1.07602 )
	);
	color *= toneMappingExposure / 0.6;
	color = ACESInputMat * color;
	color = RRTAndODTFit( color );
	color = ACESOutputMat * color;
	return saturate( color );
}
const mat3 LINEAR_REC2020_TO_LINEAR_SRGB = mat3(
	vec3( 1.6605, - 0.1246, - 0.0182 ),
	vec3( - 0.5876, 1.1329, - 0.1006 ),
	vec3( - 0.0728, - 0.0083, 1.1187 )
);
const mat3 LINEAR_SRGB_TO_LINEAR_REC2020 = mat3(
	vec3( 0.6274, 0.0691, 0.0164 ),
	vec3( 0.3293, 0.9195, 0.0880 ),
	vec3( 0.0433, 0.0113, 0.8956 )
);
vec3 agxDefaultContrastApprox( vec3 x ) {
	vec3 x2 = x * x;
	vec3 x4 = x2 * x2;
	return + 15.5 * x4 * x2
		- 40.14 * x4 * x
		+ 31.96 * x4
		- 6.868 * x2 * x
		+ 0.4298 * x2
		+ 0.1191 * x
		- 0.00232;
}
vec3 AgXToneMapping( vec3 color ) {
	const mat3 AgXInsetMatrix = mat3(
		vec3( 0.856627153315983, 0.137318972929847, 0.11189821299995 ),
		vec3( 0.0951212405381588, 0.761241990602591, 0.0767994186031903 ),
		vec3( 0.0482516061458583, 0.101439036467562, 0.811302368396859 )
	);
	const mat3 AgXOutsetMatrix = mat3(
		vec3( 1.1271005818144368, - 0.1413297634984383, - 0.14132976349843826 ),
		vec3( - 0.11060664309660323, 1.157823702216272, - 0.11060664309660294 ),
		vec3( - 0.016493938717834573, - 0.016493938717834257, 1.2519364065950405 )
	);
	const float AgxMinEv = - 12.47393;	const float AgxMaxEv = 4.026069;
	color *= toneMappingExposure;
	color = LINEAR_SRGB_TO_LINEAR_REC2020 * color;
	color = AgXInsetMatrix * color;
	color = max( color, 1e-10 );	color = log2( color );
	color = ( color - AgxMinEv ) / ( AgxMaxEv - AgxMinEv );
	color = clamp( color, 0.0, 1.0 );
	color = agxDefaultContrastApprox( color );
	color = AgXOutsetMatrix * color;
	color = pow( max( vec3( 0.0 ), color ), vec3( 2.2 ) );
	color = LINEAR_REC2020_TO_LINEAR_SRGB * color;
	color = clamp( color, 0.0, 1.0 );
	return color;
}
vec3 NeutralToneMapping( vec3 color ) {
	const float StartCompression = 0.8 - 0.04;
	const float Desaturation = 0.15;
	color *= toneMappingExposure;
	float x = min( color.r, min( color.g, color.b ) );
	float offset = x < 0.08 ? x - 6.25 * x * x : 0.04;
	color -= offset;
	float peak = max( color.r, max( color.g, color.b ) );
	if ( peak < StartCompression ) return color;
	float d = 1. - StartCompression;
	float newPeak = 1. - d * d / ( peak + d - StartCompression );
	color *= newPeak / peak;
	float g = 1. - 1. / ( Desaturation * ( peak - newPeak ) + 1. );
	return mix( color, vec3( newPeak ), g );
}
vec3 CustomToneMapping( vec3 color ) { return color; }`,_E=`#ifdef USE_TRANSMISSION
	material.transmission = transmission;
	material.transmissionAlpha = 1.0;
	material.thickness = thickness;
	material.attenuationDistance = attenuationDistance;
	material.attenuationColor = attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		material.transmission *= texture2D( transmissionMap, vTransmissionMapUv ).r;
	#endif
	#ifdef USE_THICKNESSMAP
		material.thickness *= texture2D( thicknessMap, vThicknessMapUv ).g;
	#endif
	vec3 pos = vWorldPosition;
	vec3 v = normalize( cameraPosition - pos );
	vec3 n = inverseTransformDirection( normal, viewMatrix );
	vec4 transmitted = getIBLVolumeRefraction(
		n, v, material.roughness, material.diffuseColor, material.specularColor, material.specularF90,
		pos, modelMatrix, viewMatrix, projectionMatrix, material.dispersion, material.ior, material.thickness,
		material.attenuationColor, material.attenuationDistance );
	material.transmissionAlpha = mix( material.transmissionAlpha, transmitted.a, material.transmission );
	totalDiffuse = mix( totalDiffuse, transmitted.rgb, material.transmission );
#endif`,vE=`#ifdef USE_TRANSMISSION
	uniform float transmission;
	uniform float thickness;
	uniform float attenuationDistance;
	uniform vec3 attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		uniform sampler2D transmissionMap;
	#endif
	#ifdef USE_THICKNESSMAP
		uniform sampler2D thicknessMap;
	#endif
	uniform vec2 transmissionSamplerSize;
	uniform sampler2D transmissionSamplerMap;
	uniform mat4 modelMatrix;
	uniform mat4 projectionMatrix;
	varying vec3 vWorldPosition;
	float w0( float a ) {
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - a + 3.0 ) - 3.0 ) + 1.0 );
	}
	float w1( float a ) {
		return ( 1.0 / 6.0 ) * ( a *  a * ( 3.0 * a - 6.0 ) + 4.0 );
	}
	float w2( float a ){
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - 3.0 * a + 3.0 ) + 3.0 ) + 1.0 );
	}
	float w3( float a ) {
		return ( 1.0 / 6.0 ) * ( a * a * a );
	}
	float g0( float a ) {
		return w0( a ) + w1( a );
	}
	float g1( float a ) {
		return w2( a ) + w3( a );
	}
	float h0( float a ) {
		return - 1.0 + w1( a ) / ( w0( a ) + w1( a ) );
	}
	float h1( float a ) {
		return 1.0 + w3( a ) / ( w2( a ) + w3( a ) );
	}
	vec4 bicubic( sampler2D tex, vec2 uv, vec4 texelSize, float lod ) {
		uv = uv * texelSize.zw + 0.5;
		vec2 iuv = floor( uv );
		vec2 fuv = fract( uv );
		float g0x = g0( fuv.x );
		float g1x = g1( fuv.x );
		float h0x = h0( fuv.x );
		float h1x = h1( fuv.x );
		float h0y = h0( fuv.y );
		float h1y = h1( fuv.y );
		vec2 p0 = ( vec2( iuv.x + h0x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p1 = ( vec2( iuv.x + h1x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p2 = ( vec2( iuv.x + h0x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		vec2 p3 = ( vec2( iuv.x + h1x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		return g0( fuv.y ) * ( g0x * textureLod( tex, p0, lod ) + g1x * textureLod( tex, p1, lod ) ) +
			g1( fuv.y ) * ( g0x * textureLod( tex, p2, lod ) + g1x * textureLod( tex, p3, lod ) );
	}
	vec4 textureBicubic( sampler2D sampler, vec2 uv, float lod ) {
		vec2 fLodSize = vec2( textureSize( sampler, int( lod ) ) );
		vec2 cLodSize = vec2( textureSize( sampler, int( lod + 1.0 ) ) );
		vec2 fLodSizeInv = 1.0 / fLodSize;
		vec2 cLodSizeInv = 1.0 / cLodSize;
		vec4 fSample = bicubic( sampler, uv, vec4( fLodSizeInv, fLodSize ), floor( lod ) );
		vec4 cSample = bicubic( sampler, uv, vec4( cLodSizeInv, cLodSize ), ceil( lod ) );
		return mix( fSample, cSample, fract( lod ) );
	}
	vec3 getVolumeTransmissionRay( const in vec3 n, const in vec3 v, const in float thickness, const in float ior, const in mat4 modelMatrix ) {
		vec3 refractionVector = refract( - v, normalize( n ), 1.0 / ior );
		vec3 modelScale;
		modelScale.x = length( vec3( modelMatrix[ 0 ].xyz ) );
		modelScale.y = length( vec3( modelMatrix[ 1 ].xyz ) );
		modelScale.z = length( vec3( modelMatrix[ 2 ].xyz ) );
		return normalize( refractionVector ) * thickness * modelScale;
	}
	float applyIorToRoughness( const in float roughness, const in float ior ) {
		return roughness * clamp( ior * 2.0 - 2.0, 0.0, 1.0 );
	}
	vec4 getTransmissionSample( const in vec2 fragCoord, const in float roughness, const in float ior ) {
		float lod = log2( transmissionSamplerSize.x ) * applyIorToRoughness( roughness, ior );
		return textureBicubic( transmissionSamplerMap, fragCoord.xy, lod );
	}
	vec3 volumeAttenuation( const in float transmissionDistance, const in vec3 attenuationColor, const in float attenuationDistance ) {
		if ( isinf( attenuationDistance ) ) {
			return vec3( 1.0 );
		} else {
			vec3 attenuationCoefficient = -log( attenuationColor ) / attenuationDistance;
			vec3 transmittance = exp( - attenuationCoefficient * transmissionDistance );			return transmittance;
		}
	}
	vec4 getIBLVolumeRefraction( const in vec3 n, const in vec3 v, const in float roughness, const in vec3 diffuseColor,
		const in vec3 specularColor, const in float specularF90, const in vec3 position, const in mat4 modelMatrix,
		const in mat4 viewMatrix, const in mat4 projMatrix, const in float dispersion, const in float ior, const in float thickness,
		const in vec3 attenuationColor, const in float attenuationDistance ) {
		vec4 transmittedLight;
		vec3 transmittance;
		#ifdef USE_DISPERSION
			float halfSpread = ( ior - 1.0 ) * 0.025 * dispersion;
			vec3 iors = vec3( ior - halfSpread, ior, ior + halfSpread );
			for ( int i = 0; i < 3; i ++ ) {
				vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, iors[ i ], modelMatrix );
				vec3 refractedRayExit = position + transmissionRay;
				vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
				vec2 refractionCoords = ndcPos.xy / ndcPos.w;
				refractionCoords += 1.0;
				refractionCoords /= 2.0;
				vec4 transmissionSample = getTransmissionSample( refractionCoords, roughness, iors[ i ] );
				transmittedLight[ i ] = transmissionSample[ i ];
				transmittedLight.a += transmissionSample.a;
				transmittance[ i ] = diffuseColor[ i ] * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance )[ i ];
			}
			transmittedLight.a /= 3.0;
		#else
			vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, ior, modelMatrix );
			vec3 refractedRayExit = position + transmissionRay;
			vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
			vec2 refractionCoords = ndcPos.xy / ndcPos.w;
			refractionCoords += 1.0;
			refractionCoords /= 2.0;
			transmittedLight = getTransmissionSample( refractionCoords, roughness, ior );
			transmittance = diffuseColor * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance );
		#endif
		vec3 attenuatedColor = transmittance * transmittedLight.rgb;
		vec3 F = EnvironmentBRDF( n, v, specularColor, specularF90, roughness );
		float transmittanceFactor = ( transmittance.r + transmittance.g + transmittance.b ) / 3.0;
		return vec4( ( 1.0 - F ) * attenuatedColor, 1.0 - ( 1.0 - transmittedLight.a ) * transmittanceFactor );
	}
#endif`,xE=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_SPECULARMAP
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,wE=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	uniform mat3 mapTransform;
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	uniform mat3 alphaMapTransform;
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	uniform mat3 lightMapTransform;
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	uniform mat3 aoMapTransform;
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	uniform mat3 bumpMapTransform;
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	uniform mat3 normalMapTransform;
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_DISPLACEMENTMAP
	uniform mat3 displacementMapTransform;
	varying vec2 vDisplacementMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	uniform mat3 emissiveMapTransform;
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	uniform mat3 metalnessMapTransform;
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	uniform mat3 roughnessMapTransform;
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	uniform mat3 anisotropyMapTransform;
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	uniform mat3 clearcoatMapTransform;
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform mat3 clearcoatNormalMapTransform;
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform mat3 clearcoatRoughnessMapTransform;
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	uniform mat3 sheenColorMapTransform;
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	uniform mat3 sheenRoughnessMapTransform;
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	uniform mat3 iridescenceMapTransform;
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform mat3 iridescenceThicknessMapTransform;
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SPECULARMAP
	uniform mat3 specularMapTransform;
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	uniform mat3 specularColorMapTransform;
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	uniform mat3 specularIntensityMapTransform;
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,yE=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	vUv = vec3( uv, 1 ).xy;
#endif
#ifdef USE_MAP
	vMapUv = ( mapTransform * vec3( MAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ALPHAMAP
	vAlphaMapUv = ( alphaMapTransform * vec3( ALPHAMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_LIGHTMAP
	vLightMapUv = ( lightMapTransform * vec3( LIGHTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_AOMAP
	vAoMapUv = ( aoMapTransform * vec3( AOMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_BUMPMAP
	vBumpMapUv = ( bumpMapTransform * vec3( BUMPMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_NORMALMAP
	vNormalMapUv = ( normalMapTransform * vec3( NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_DISPLACEMENTMAP
	vDisplacementMapUv = ( displacementMapTransform * vec3( DISPLACEMENTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_EMISSIVEMAP
	vEmissiveMapUv = ( emissiveMapTransform * vec3( EMISSIVEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_METALNESSMAP
	vMetalnessMapUv = ( metalnessMapTransform * vec3( METALNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ROUGHNESSMAP
	vRoughnessMapUv = ( roughnessMapTransform * vec3( ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ANISOTROPYMAP
	vAnisotropyMapUv = ( anisotropyMapTransform * vec3( ANISOTROPYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOATMAP
	vClearcoatMapUv = ( clearcoatMapTransform * vec3( CLEARCOATMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	vClearcoatNormalMapUv = ( clearcoatNormalMapTransform * vec3( CLEARCOAT_NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	vClearcoatRoughnessMapUv = ( clearcoatRoughnessMapTransform * vec3( CLEARCOAT_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCEMAP
	vIridescenceMapUv = ( iridescenceMapTransform * vec3( IRIDESCENCEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	vIridescenceThicknessMapUv = ( iridescenceThicknessMapTransform * vec3( IRIDESCENCE_THICKNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_COLORMAP
	vSheenColorMapUv = ( sheenColorMapTransform * vec3( SHEEN_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	vSheenRoughnessMapUv = ( sheenRoughnessMapTransform * vec3( SHEEN_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULARMAP
	vSpecularMapUv = ( specularMapTransform * vec3( SPECULARMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_COLORMAP
	vSpecularColorMapUv = ( specularColorMapTransform * vec3( SPECULAR_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	vSpecularIntensityMapUv = ( specularIntensityMapTransform * vec3( SPECULAR_INTENSITYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_TRANSMISSIONMAP
	vTransmissionMapUv = ( transmissionMapTransform * vec3( TRANSMISSIONMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_THICKNESSMAP
	vThicknessMapUv = ( thicknessMapTransform * vec3( THICKNESSMAP_UV, 1 ) ).xy;
#endif`,bE=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const SE=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,EE=`uniform sampler2D t2D;
uniform float backgroundIntensity;
varying vec2 vUv;
void main() {
	vec4 texColor = texture2D( t2D, vUv );
	#ifdef DECODE_VIDEO_TEXTURE
		texColor = vec4( mix( pow( texColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), texColor.rgb * 0.0773993808, vec3( lessThanEqual( texColor.rgb, vec3( 0.04045 ) ) ) ), texColor.w );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,ME=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,TE=`#ifdef ENVMAP_TYPE_CUBE
	uniform samplerCube envMap;
#elif defined( ENVMAP_TYPE_CUBE_UV )
	uniform sampler2D envMap;
#endif
uniform float flipEnvMap;
uniform float backgroundBlurriness;
uniform float backgroundIntensity;
uniform mat3 backgroundRotation;
varying vec3 vWorldDirection;
#include <cube_uv_reflection_fragment>
void main() {
	#ifdef ENVMAP_TYPE_CUBE
		vec4 texColor = textureCube( envMap, backgroundRotation * vec3( flipEnvMap * vWorldDirection.x, vWorldDirection.yz ) );
	#elif defined( ENVMAP_TYPE_CUBE_UV )
		vec4 texColor = textureCubeUV( envMap, backgroundRotation * vWorldDirection, backgroundBlurriness );
	#else
		vec4 texColor = vec4( 0.0, 0.0, 0.0, 1.0 );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,AE=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,CE=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,PE=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
varying vec2 vHighPrecisionZW;
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vHighPrecisionZW = gl_Position.zw;
}`,RE=`#if DEPTH_PACKING == 3200
	uniform float opacity;
#endif
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
varying vec2 vHighPrecisionZW;
void main() {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#if DEPTH_PACKING == 3200
		diffuseColor.a = opacity;
	#endif
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <logdepthbuf_fragment>
	#ifdef USE_REVERSED_DEPTH_BUFFER
		float fragCoordZ = vHighPrecisionZW[ 0 ] / vHighPrecisionZW[ 1 ];
	#else
		float fragCoordZ = 0.5 * vHighPrecisionZW[ 0 ] / vHighPrecisionZW[ 1 ] + 0.5;
	#endif
	#if DEPTH_PACKING == 3200
		gl_FragColor = vec4( vec3( 1.0 - fragCoordZ ), opacity );
	#elif DEPTH_PACKING == 3201
		gl_FragColor = packDepthToRGBA( fragCoordZ );
	#elif DEPTH_PACKING == 3202
		gl_FragColor = vec4( packDepthToRGB( fragCoordZ ), 1.0 );
	#elif DEPTH_PACKING == 3203
		gl_FragColor = vec4( packDepthToRG( fragCoordZ ), 0.0, 1.0 );
	#endif
}`,DE=`#define DISTANCE
varying vec3 vWorldPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <worldpos_vertex>
	#include <clipping_planes_vertex>
	vWorldPosition = worldPosition.xyz;
}`,LE=`#define DISTANCE
uniform vec3 referencePosition;
uniform float nearDistance;
uniform float farDistance;
varying vec3 vWorldPosition;
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <clipping_planes_pars_fragment>
void main () {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	float dist = length( vWorldPosition - referencePosition );
	dist = ( dist - nearDistance ) / ( farDistance - nearDistance );
	dist = saturate( dist );
	gl_FragColor = packDepthToRGBA( dist );
}`,IE=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,UE=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,OE=`uniform float scale;
attribute float lineDistance;
varying float vLineDistance;
#include <common>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	vLineDistance = scale * lineDistance;
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,FE=`uniform vec3 diffuse;
uniform float opacity;
uniform float dashSize;
uniform float totalSize;
varying float vLineDistance;
#include <common>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	if ( mod( vLineDistance, totalSize ) > dashSize ) {
		discard;
	}
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,NE=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#if defined ( USE_ENVMAP ) || defined ( USE_SKINNING )
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinbase_vertex>
		#include <skinnormal_vertex>
		#include <defaultnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <fog_vertex>
}`,kE=`uniform vec3 diffuse;
uniform float opacity;
#ifndef FLAT_SHADED
	varying vec3 vNormal;
#endif
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		reflectedLight.indirectDiffuse += lightMapTexel.rgb * lightMapIntensity * RECIPROCAL_PI;
	#else
		reflectedLight.indirectDiffuse += vec3( 1.0 );
	#endif
	#include <aomap_fragment>
	reflectedLight.indirectDiffuse *= diffuseColor.rgb;
	vec3 outgoingLight = reflectedLight.indirectDiffuse;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,BE=`#define LAMBERT
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,zE=`#define LAMBERT
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_lambert_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_lambert_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,VE=`#define MATCAP
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <displacementmap_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
	vViewPosition = - mvPosition.xyz;
}`,HE=`#define MATCAP
uniform vec3 diffuse;
uniform float opacity;
uniform sampler2D matcap;
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	vec3 viewDir = normalize( vViewPosition );
	vec3 x = normalize( vec3( viewDir.z, 0.0, - viewDir.x ) );
	vec3 y = cross( viewDir, x );
	vec2 uv = vec2( dot( x, normal ), dot( y, normal ) ) * 0.495 + 0.5;
	#ifdef USE_MATCAP
		vec4 matcapColor = texture2D( matcap, uv );
	#else
		vec4 matcapColor = vec4( vec3( mix( 0.2, 0.8, uv.y ) ), 1.0 );
	#endif
	vec3 outgoingLight = diffuseColor.rgb * matcapColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,GE=`#define NORMAL
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	vViewPosition = - mvPosition.xyz;
#endif
}`,WE=`#define NORMAL
uniform float opacity;
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <packing>
#include <uv_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( 0.0, 0.0, 0.0, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	gl_FragColor = vec4( packNormalToRGB( normal ), diffuseColor.a );
	#ifdef OPAQUE
		gl_FragColor.a = 1.0;
	#endif
}`,XE=`#define PHONG
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,$E=`#define PHONG
uniform vec3 diffuse;
uniform vec3 emissive;
uniform vec3 specular;
uniform float shininess;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_phong_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_phong_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,qE=`#define STANDARD
varying vec3 vViewPosition;
#ifdef USE_TRANSMISSION
	varying vec3 vWorldPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
#ifdef USE_TRANSMISSION
	vWorldPosition = worldPosition.xyz;
#endif
}`,YE=`#define STANDARD
#ifdef PHYSICAL
	#define IOR
	#define USE_SPECULAR
#endif
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float roughness;
uniform float metalness;
uniform float opacity;
#ifdef IOR
	uniform float ior;
#endif
#ifdef USE_SPECULAR
	uniform float specularIntensity;
	uniform vec3 specularColor;
	#ifdef USE_SPECULAR_COLORMAP
		uniform sampler2D specularColorMap;
	#endif
	#ifdef USE_SPECULAR_INTENSITYMAP
		uniform sampler2D specularIntensityMap;
	#endif
#endif
#ifdef USE_CLEARCOAT
	uniform float clearcoat;
	uniform float clearcoatRoughness;
#endif
#ifdef USE_DISPERSION
	uniform float dispersion;
#endif
#ifdef USE_IRIDESCENCE
	uniform float iridescence;
	uniform float iridescenceIOR;
	uniform float iridescenceThicknessMinimum;
	uniform float iridescenceThicknessMaximum;
#endif
#ifdef USE_SHEEN
	uniform vec3 sheenColor;
	uniform float sheenRoughness;
	#ifdef USE_SHEEN_COLORMAP
		uniform sampler2D sheenColorMap;
	#endif
	#ifdef USE_SHEEN_ROUGHNESSMAP
		uniform sampler2D sheenRoughnessMap;
	#endif
#endif
#ifdef USE_ANISOTROPY
	uniform vec2 anisotropyVector;
	#ifdef USE_ANISOTROPYMAP
		uniform sampler2D anisotropyMap;
	#endif
#endif
varying vec3 vViewPosition;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <iridescence_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_physical_pars_fragment>
#include <transmission_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <clearcoat_pars_fragment>
#include <iridescence_pars_fragment>
#include <roughnessmap_pars_fragment>
#include <metalnessmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <roughnessmap_fragment>
	#include <metalnessmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <clearcoat_normal_fragment_begin>
	#include <clearcoat_normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_physical_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 totalDiffuse = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse;
	vec3 totalSpecular = reflectedLight.directSpecular + reflectedLight.indirectSpecular;
	#include <transmission_fragment>
	vec3 outgoingLight = totalDiffuse + totalSpecular + totalEmissiveRadiance;
	#ifdef USE_SHEEN
		float sheenEnergyComp = 1.0 - 0.157 * max3( material.sheenColor );
		outgoingLight = outgoingLight * sheenEnergyComp + sheenSpecularDirect + sheenSpecularIndirect;
	#endif
	#ifdef USE_CLEARCOAT
		float dotNVcc = saturate( dot( geometryClearcoatNormal, geometryViewDir ) );
		vec3 Fcc = F_Schlick( material.clearcoatF0, material.clearcoatF90, dotNVcc );
		outgoingLight = outgoingLight * ( 1.0 - material.clearcoat * Fcc ) + ( clearcoatSpecularDirect + clearcoatSpecularIndirect ) * material.clearcoat;
	#endif
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,jE=`#define TOON
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,KE=`#define TOON
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <gradientmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_toon_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_toon_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,ZE=`uniform float size;
uniform float scale;
#include <common>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
#ifdef USE_POINTS_UV
	varying vec2 vUv;
	uniform mat3 uvTransform;
#endif
void main() {
	#ifdef USE_POINTS_UV
		vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	#endif
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	gl_PointSize = size;
	#ifdef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) gl_PointSize *= ( scale / - mvPosition.z );
	#endif
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <fog_vertex>
}`,JE=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <color_pars_fragment>
#include <map_particle_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_particle_fragment>
	#include <color_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,QE=`#include <common>
#include <batching_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <shadowmap_pars_vertex>
void main() {
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,eM=`uniform vec3 color;
uniform float opacity;
#include <common>
#include <packing>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <logdepthbuf_pars_fragment>
#include <shadowmap_pars_fragment>
#include <shadowmask_pars_fragment>
void main() {
	#include <logdepthbuf_fragment>
	gl_FragColor = vec4( color, opacity * ( 1.0 - getShadowMask() ) );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,tM=`uniform float rotation;
uniform vec2 center;
#include <common>
#include <uv_pars_vertex>
#include <fog_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	vec4 mvPosition = modelViewMatrix[ 3 ];
	vec2 scale = vec2( length( modelMatrix[ 0 ].xyz ), length( modelMatrix[ 1 ].xyz ) );
	#ifndef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) scale *= - mvPosition.z;
	#endif
	vec2 alignedPosition = ( position.xy - ( center - vec2( 0.5 ) ) ) * scale;
	vec2 rotatedPosition;
	rotatedPosition.x = cos( rotation ) * alignedPosition.x - sin( rotation ) * alignedPosition.y;
	rotatedPosition.y = sin( rotation ) * alignedPosition.x + cos( rotation ) * alignedPosition.y;
	mvPosition.xy += rotatedPosition;
	gl_Position = projectionMatrix * mvPosition;
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,nM=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,ke={alphahash_fragment:Eb,alphahash_pars_fragment:Mb,alphamap_fragment:Tb,alphamap_pars_fragment:Ab,alphatest_fragment:Cb,alphatest_pars_fragment:Pb,aomap_fragment:Rb,aomap_pars_fragment:Db,batching_pars_vertex:Lb,batching_vertex:Ib,begin_vertex:Ub,beginnormal_vertex:Ob,bsdfs:Fb,iridescence_fragment:Nb,bumpmap_pars_fragment:kb,clipping_planes_fragment:Bb,clipping_planes_pars_fragment:zb,clipping_planes_pars_vertex:Vb,clipping_planes_vertex:Hb,color_fragment:Gb,color_pars_fragment:Wb,color_pars_vertex:Xb,color_vertex:$b,common:qb,cube_uv_reflection_fragment:Yb,defaultnormal_vertex:jb,displacementmap_pars_vertex:Kb,displacementmap_vertex:Zb,emissivemap_fragment:Jb,emissivemap_pars_fragment:Qb,colorspace_fragment:eS,colorspace_pars_fragment:tS,envmap_fragment:nS,envmap_common_pars_fragment:iS,envmap_pars_fragment:rS,envmap_pars_vertex:sS,envmap_physical_pars_fragment:gS,envmap_vertex:oS,fog_vertex:aS,fog_pars_vertex:lS,fog_fragment:cS,fog_pars_fragment:uS,gradientmap_pars_fragment:dS,lightmap_pars_fragment:hS,lights_lambert_fragment:fS,lights_lambert_pars_fragment:pS,lights_pars_begin:mS,lights_toon_fragment:_S,lights_toon_pars_fragment:vS,lights_phong_fragment:xS,lights_phong_pars_fragment:wS,lights_physical_fragment:yS,lights_physical_pars_fragment:bS,lights_fragment_begin:SS,lights_fragment_maps:ES,lights_fragment_end:MS,logdepthbuf_fragment:TS,logdepthbuf_pars_fragment:AS,logdepthbuf_pars_vertex:CS,logdepthbuf_vertex:PS,map_fragment:RS,map_pars_fragment:DS,map_particle_fragment:LS,map_particle_pars_fragment:IS,metalnessmap_fragment:US,metalnessmap_pars_fragment:OS,morphinstance_vertex:FS,morphcolor_vertex:NS,morphnormal_vertex:kS,morphtarget_pars_vertex:BS,morphtarget_vertex:zS,normal_fragment_begin:VS,normal_fragment_maps:HS,normal_pars_fragment:GS,normal_pars_vertex:WS,normal_vertex:XS,normalmap_pars_fragment:$S,clearcoat_normal_fragment_begin:qS,clearcoat_normal_fragment_maps:YS,clearcoat_pars_fragment:jS,iridescence_pars_fragment:KS,opaque_fragment:ZS,packing:JS,premultiplied_alpha_fragment:QS,project_vertex:eE,dithering_fragment:tE,dithering_pars_fragment:nE,roughnessmap_fragment:iE,roughnessmap_pars_fragment:rE,shadowmap_pars_fragment:sE,shadowmap_pars_vertex:oE,shadowmap_vertex:aE,shadowmask_pars_fragment:lE,skinbase_vertex:cE,skinning_pars_vertex:uE,skinning_vertex:dE,skinnormal_vertex:hE,specularmap_fragment:fE,specularmap_pars_fragment:pE,tonemapping_fragment:mE,tonemapping_pars_fragment:gE,transmission_fragment:_E,transmission_pars_fragment:vE,uv_pars_fragment:xE,uv_pars_vertex:wE,uv_vertex:yE,worldpos_vertex:bE,background_vert:SE,background_frag:EE,backgroundCube_vert:ME,backgroundCube_frag:TE,cube_vert:AE,cube_frag:CE,depth_vert:PE,depth_frag:RE,distanceRGBA_vert:DE,distanceRGBA_frag:LE,equirect_vert:IE,equirect_frag:UE,linedashed_vert:OE,linedashed_frag:FE,meshbasic_vert:NE,meshbasic_frag:kE,meshlambert_vert:BE,meshlambert_frag:zE,meshmatcap_vert:VE,meshmatcap_frag:HE,meshnormal_vert:GE,meshnormal_frag:WE,meshphong_vert:XE,meshphong_frag:$E,meshphysical_vert:qE,meshphysical_frag:YE,meshtoon_vert:jE,meshtoon_frag:KE,points_vert:ZE,points_frag:JE,shadow_vert:QE,shadow_frag:eM,sprite_vert:tM,sprite_frag:nM},ae={common:{diffuse:{value:new Ze(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new Fe},alphaMap:{value:null},alphaMapTransform:{value:new Fe},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new Fe}},envmap:{envMap:{value:null},envMapRotation:{value:new Fe},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new Fe}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new Fe}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new Fe},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new Fe},normalScale:{value:new Be(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new Fe},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new Fe}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new Fe}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new Fe}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new Ze(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new Ze(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new Fe},alphaTest:{value:0},uvTransform:{value:new Fe}},sprite:{diffuse:{value:new Ze(16777215)},opacity:{value:1},center:{value:new Be(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new Fe},alphaMap:{value:null},alphaMapTransform:{value:new Fe},alphaTest:{value:0}}},Gn={basic:{uniforms:Xt([ae.common,ae.specularmap,ae.envmap,ae.aomap,ae.lightmap,ae.fog]),vertexShader:ke.meshbasic_vert,fragmentShader:ke.meshbasic_frag},lambert:{uniforms:Xt([ae.common,ae.specularmap,ae.envmap,ae.aomap,ae.lightmap,ae.emissivemap,ae.bumpmap,ae.normalmap,ae.displacementmap,ae.fog,ae.lights,{emissive:{value:new Ze(0)}}]),vertexShader:ke.meshlambert_vert,fragmentShader:ke.meshlambert_frag},phong:{uniforms:Xt([ae.common,ae.specularmap,ae.envmap,ae.aomap,ae.lightmap,ae.emissivemap,ae.bumpmap,ae.normalmap,ae.displacementmap,ae.fog,ae.lights,{emissive:{value:new Ze(0)},specular:{value:new Ze(1118481)},shininess:{value:30}}]),vertexShader:ke.meshphong_vert,fragmentShader:ke.meshphong_frag},standard:{uniforms:Xt([ae.common,ae.envmap,ae.aomap,ae.lightmap,ae.emissivemap,ae.bumpmap,ae.normalmap,ae.displacementmap,ae.roughnessmap,ae.metalnessmap,ae.fog,ae.lights,{emissive:{value:new Ze(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:ke.meshphysical_vert,fragmentShader:ke.meshphysical_frag},toon:{uniforms:Xt([ae.common,ae.aomap,ae.lightmap,ae.emissivemap,ae.bumpmap,ae.normalmap,ae.displacementmap,ae.gradientmap,ae.fog,ae.lights,{emissive:{value:new Ze(0)}}]),vertexShader:ke.meshtoon_vert,fragmentShader:ke.meshtoon_frag},matcap:{uniforms:Xt([ae.common,ae.bumpmap,ae.normalmap,ae.displacementmap,ae.fog,{matcap:{value:null}}]),vertexShader:ke.meshmatcap_vert,fragmentShader:ke.meshmatcap_frag},points:{uniforms:Xt([ae.points,ae.fog]),vertexShader:ke.points_vert,fragmentShader:ke.points_frag},dashed:{uniforms:Xt([ae.common,ae.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:ke.linedashed_vert,fragmentShader:ke.linedashed_frag},depth:{uniforms:Xt([ae.common,ae.displacementmap]),vertexShader:ke.depth_vert,fragmentShader:ke.depth_frag},normal:{uniforms:Xt([ae.common,ae.bumpmap,ae.normalmap,ae.displacementmap,{opacity:{value:1}}]),vertexShader:ke.meshnormal_vert,fragmentShader:ke.meshnormal_frag},sprite:{uniforms:Xt([ae.sprite,ae.fog]),vertexShader:ke.sprite_vert,fragmentShader:ke.sprite_frag},background:{uniforms:{uvTransform:{value:new Fe},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:ke.background_vert,fragmentShader:ke.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new Fe}},vertexShader:ke.backgroundCube_vert,fragmentShader:ke.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:ke.cube_vert,fragmentShader:ke.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:ke.equirect_vert,fragmentShader:ke.equirect_frag},distanceRGBA:{uniforms:Xt([ae.common,ae.displacementmap,{referencePosition:{value:new B},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:ke.distanceRGBA_vert,fragmentShader:ke.distanceRGBA_frag},shadow:{uniforms:Xt([ae.lights,ae.fog,{color:{value:new Ze(0)},opacity:{value:1}}]),vertexShader:ke.shadow_vert,fragmentShader:ke.shadow_frag}};Gn.physical={uniforms:Xt([Gn.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new Fe},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new Fe},clearcoatNormalScale:{value:new Be(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new Fe},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new Fe},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new Fe},sheen:{value:0},sheenColor:{value:new Ze(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new Fe},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new Fe},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new Fe},transmissionSamplerSize:{value:new Be},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new Fe},attenuationDistance:{value:0},attenuationColor:{value:new Ze(0)},specularColor:{value:new Ze(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new Fe},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new Fe},anisotropyVector:{value:new Be},anisotropyMap:{value:null},anisotropyMapTransform:{value:new Fe}}]),vertexShader:ke.meshphysical_vert,fragmentShader:ke.meshphysical_frag};const $o={r:0,b:0,g:0},Qi=new vi,iM=new Tt;function rM(n,e,t,i,r,s,o){const a=new Ze(0);let l=s===!0?0:1,c,u,d=null,p=0,f=null;function _(x){let w=x.isScene===!0?x.background:null;return w&&w.isTexture&&(w=(x.backgroundBlurriness>0?t:e).get(w)),w}function g(x){let w=!1;const S=_(x);S===null?h(a,l):S&&S.isColor&&(h(S,1),w=!0);const C=n.xr.getEnvironmentBlendMode();C==="additive"?i.buffers.color.setClear(0,0,0,1,o):C==="alpha-blend"&&i.buffers.color.setClear(0,0,0,0,o),(n.autoClear||w)&&(i.buffers.depth.setTest(!0),i.buffers.depth.setMask(!0),i.buffers.color.setMask(!0),n.clear(n.autoClearColor,n.autoClearDepth,n.autoClearStencil))}function m(x,w){const S=_(w);S&&(S.isCubeTexture||S.mapping===Ba)?(u===void 0&&(u=new jn(new Ss(1,1,1),new ti({name:"BackgroundCubeMaterial",uniforms:cs(Gn.backgroundCube.uniforms),vertexShader:Gn.backgroundCube.vertexShader,fragmentShader:Gn.backgroundCube.fragmentShader,side:qt,depthTest:!1,depthWrite:!1,fog:!1,allowOverride:!1})),u.geometry.deleteAttribute("normal"),u.geometry.deleteAttribute("uv"),u.onBeforeRender=function(C,T,A){this.matrixWorld.copyPosition(A.matrixWorld)},Object.defineProperty(u.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),r.update(u)),Qi.copy(w.backgroundRotation),Qi.x*=-1,Qi.y*=-1,Qi.z*=-1,S.isCubeTexture&&S.isRenderTargetTexture===!1&&(Qi.y*=-1,Qi.z*=-1),u.material.uniforms.envMap.value=S,u.material.uniforms.flipEnvMap.value=S.isCubeTexture&&S.isRenderTargetTexture===!1?-1:1,u.material.uniforms.backgroundBlurriness.value=w.backgroundBlurriness,u.material.uniforms.backgroundIntensity.value=w.backgroundIntensity,u.material.uniforms.backgroundRotation.value.setFromMatrix4(iM.makeRotationFromEuler(Qi)),u.material.toneMapped=qe.getTransfer(S.colorSpace)!==et,(d!==S||p!==S.version||f!==n.toneMapping)&&(u.material.needsUpdate=!0,d=S,p=S.version,f=n.toneMapping),u.layers.enableAll(),x.unshift(u,u.geometry,u.material,0,0,null)):S&&S.isTexture&&(c===void 0&&(c=new jn(new Va(2,2),new ti({name:"BackgroundMaterial",uniforms:cs(Gn.background.uniforms),vertexShader:Gn.background.vertexShader,fragmentShader:Gn.background.fragmentShader,side:Hi,depthTest:!1,depthWrite:!1,fog:!1,allowOverride:!1})),c.geometry.deleteAttribute("normal"),Object.defineProperty(c.material,"map",{get:function(){return this.uniforms.t2D.value}}),r.update(c)),c.material.uniforms.t2D.value=S,c.material.uniforms.backgroundIntensity.value=w.backgroundIntensity,c.material.toneMapped=qe.getTransfer(S.colorSpace)!==et,S.matrixAutoUpdate===!0&&S.updateMatrix(),c.material.uniforms.uvTransform.value.copy(S.matrix),(d!==S||p!==S.version||f!==n.toneMapping)&&(c.material.needsUpdate=!0,d=S,p=S.version,f=n.toneMapping),c.layers.enableAll(),x.unshift(c,c.geometry,c.material,0,0,null))}function h(x,w){x.getRGB($o,rm(n)),i.buffers.color.setClear($o.r,$o.g,$o.b,w,o)}function v(){u!==void 0&&(u.geometry.dispose(),u.material.dispose(),u=void 0),c!==void 0&&(c.geometry.dispose(),c.material.dispose(),c=void 0)}return{getClearColor:function(){return a},setClearColor:function(x,w=1){a.set(x),l=w,h(a,l)},getClearAlpha:function(){return l},setClearAlpha:function(x){l=x,h(a,l)},render:g,addToRenderList:m,dispose:v}}function sM(n,e){const t=n.getParameter(n.MAX_VERTEX_ATTRIBS),i={},r=p(null);let s=r,o=!1;function a(y,P,D,O,V){let k=!1;const G=d(O,D,P);s!==G&&(s=G,c(s.object)),k=f(y,O,D,V),k&&_(y,O,D,V),V!==null&&e.update(V,n.ELEMENT_ARRAY_BUFFER),(k||o)&&(o=!1,w(y,P,D,O),V!==null&&n.bindBuffer(n.ELEMENT_ARRAY_BUFFER,e.get(V).buffer))}function l(){return n.createVertexArray()}function c(y){return n.bindVertexArray(y)}function u(y){return n.deleteVertexArray(y)}function d(y,P,D){const O=D.wireframe===!0;let V=i[y.id];V===void 0&&(V={},i[y.id]=V);let k=V[P.id];k===void 0&&(k={},V[P.id]=k);let G=k[O];return G===void 0&&(G=p(l()),k[O]=G),G}function p(y){const P=[],D=[],O=[];for(let V=0;V<t;V++)P[V]=0,D[V]=0,O[V]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:P,enabledAttributes:D,attributeDivisors:O,object:y,attributes:{},index:null}}function f(y,P,D,O){const V=s.attributes,k=P.attributes;let G=0;const $=D.getAttributes();for(const U in $)if($[U].location>=0){const ee=V[U];let ce=k[U];if(ce===void 0&&(U==="instanceMatrix"&&y.instanceMatrix&&(ce=y.instanceMatrix),U==="instanceColor"&&y.instanceColor&&(ce=y.instanceColor)),ee===void 0||ee.attribute!==ce||ce&&ee.data!==ce.data)return!0;G++}return s.attributesNum!==G||s.index!==O}function _(y,P,D,O){const V={},k=P.attributes;let G=0;const $=D.getAttributes();for(const U in $)if($[U].location>=0){let ee=k[U];ee===void 0&&(U==="instanceMatrix"&&y.instanceMatrix&&(ee=y.instanceMatrix),U==="instanceColor"&&y.instanceColor&&(ee=y.instanceColor));const ce={};ce.attribute=ee,ee&&ee.data&&(ce.data=ee.data),V[U]=ce,G++}s.attributes=V,s.attributesNum=G,s.index=O}function g(){const y=s.newAttributes;for(let P=0,D=y.length;P<D;P++)y[P]=0}function m(y){h(y,0)}function h(y,P){const D=s.newAttributes,O=s.enabledAttributes,V=s.attributeDivisors;D[y]=1,O[y]===0&&(n.enableVertexAttribArray(y),O[y]=1),V[y]!==P&&(n.vertexAttribDivisor(y,P),V[y]=P)}function v(){const y=s.newAttributes,P=s.enabledAttributes;for(let D=0,O=P.length;D<O;D++)P[D]!==y[D]&&(n.disableVertexAttribArray(D),P[D]=0)}function x(y,P,D,O,V,k,G){G===!0?n.vertexAttribIPointer(y,P,D,V,k):n.vertexAttribPointer(y,P,D,O,V,k)}function w(y,P,D,O){g();const V=O.attributes,k=D.getAttributes(),G=P.defaultAttributeValues;for(const $ in k){const U=k[$];if(U.location>=0){let Z=V[$];if(Z===void 0&&($==="instanceMatrix"&&y.instanceMatrix&&(Z=y.instanceMatrix),$==="instanceColor"&&y.instanceColor&&(Z=y.instanceColor)),Z!==void 0){const ee=Z.normalized,ce=Z.itemSize,Ae=e.get(Z);if(Ae===void 0)continue;const Je=Ae.buffer,We=Ae.type,ze=Ae.bytesPerElement,j=We===n.INT||We===n.UNSIGNED_INT||Z.gpuType===Hu;if(Z.isInterleavedBufferAttribute){const Q=Z.data,pe=Q.stride,Le=Z.offset;if(Q.isInstancedInterleavedBuffer){for(let Se=0;Se<U.locationSize;Se++)h(U.location+Se,Q.meshPerAttribute);y.isInstancedMesh!==!0&&O._maxInstanceCount===void 0&&(O._maxInstanceCount=Q.meshPerAttribute*Q.count)}else for(let Se=0;Se<U.locationSize;Se++)m(U.location+Se);n.bindBuffer(n.ARRAY_BUFFER,Je);for(let Se=0;Se<U.locationSize;Se++)x(U.location+Se,ce/U.locationSize,We,ee,pe*ze,(Le+ce/U.locationSize*Se)*ze,j)}else{if(Z.isInstancedBufferAttribute){for(let Q=0;Q<U.locationSize;Q++)h(U.location+Q,Z.meshPerAttribute);y.isInstancedMesh!==!0&&O._maxInstanceCount===void 0&&(O._maxInstanceCount=Z.meshPerAttribute*Z.count)}else for(let Q=0;Q<U.locationSize;Q++)m(U.location+Q);n.bindBuffer(n.ARRAY_BUFFER,Je);for(let Q=0;Q<U.locationSize;Q++)x(U.location+Q,ce/U.locationSize,We,ee,ce*ze,ce/U.locationSize*Q*ze,j)}}else if(G!==void 0){const ee=G[$];if(ee!==void 0)switch(ee.length){case 2:n.vertexAttrib2fv(U.location,ee);break;case 3:n.vertexAttrib3fv(U.location,ee);break;case 4:n.vertexAttrib4fv(U.location,ee);break;default:n.vertexAttrib1fv(U.location,ee)}}}}v()}function S(){A();for(const y in i){const P=i[y];for(const D in P){const O=P[D];for(const V in O)u(O[V].object),delete O[V];delete P[D]}delete i[y]}}function C(y){if(i[y.id]===void 0)return;const P=i[y.id];for(const D in P){const O=P[D];for(const V in O)u(O[V].object),delete O[V];delete P[D]}delete i[y.id]}function T(y){for(const P in i){const D=i[P];if(D[y.id]===void 0)continue;const O=D[y.id];for(const V in O)u(O[V].object),delete O[V];delete D[y.id]}}function A(){b(),o=!0,s!==r&&(s=r,c(s.object))}function b(){r.geometry=null,r.program=null,r.wireframe=!1}return{setup:a,reset:A,resetDefaultState:b,dispose:S,releaseStatesOfGeometry:C,releaseStatesOfProgram:T,initAttributes:g,enableAttribute:m,disableUnusedAttributes:v}}function oM(n,e,t){let i;function r(c){i=c}function s(c,u){n.drawArrays(i,c,u),t.update(u,i,1)}function o(c,u,d){d!==0&&(n.drawArraysInstanced(i,c,u,d),t.update(u,i,d))}function a(c,u,d){if(d===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(i,c,0,u,0,d);let f=0;for(let _=0;_<d;_++)f+=u[_];t.update(f,i,1)}function l(c,u,d,p){if(d===0)return;const f=e.get("WEBGL_multi_draw");if(f===null)for(let _=0;_<c.length;_++)o(c[_],u[_],p[_]);else{f.multiDrawArraysInstancedWEBGL(i,c,0,u,0,p,0,d);let _=0;for(let g=0;g<d;g++)_+=u[g]*p[g];t.update(_,i,1)}}this.setMode=r,this.render=s,this.renderInstances=o,this.renderMultiDraw=a,this.renderMultiDrawInstances=l}function aM(n,e,t,i){let r;function s(){if(r!==void 0)return r;if(e.has("EXT_texture_filter_anisotropic")===!0){const T=e.get("EXT_texture_filter_anisotropic");r=n.getParameter(T.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else r=0;return r}function o(T){return!(T!==Nn&&i.convert(T)!==n.getParameter(n.IMPLEMENTATION_COLOR_READ_FORMAT))}function a(T){const A=T===go&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(T!==_i&&i.convert(T)!==n.getParameter(n.IMPLEMENTATION_COLOR_READ_TYPE)&&T!==fi&&!A)}function l(T){if(T==="highp"){if(n.getShaderPrecisionFormat(n.VERTEX_SHADER,n.HIGH_FLOAT).precision>0&&n.getShaderPrecisionFormat(n.FRAGMENT_SHADER,n.HIGH_FLOAT).precision>0)return"highp";T="mediump"}return T==="mediump"&&n.getShaderPrecisionFormat(n.VERTEX_SHADER,n.MEDIUM_FLOAT).precision>0&&n.getShaderPrecisionFormat(n.FRAGMENT_SHADER,n.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let c=t.precision!==void 0?t.precision:"highp";const u=l(c);u!==c&&(console.warn("THREE.WebGLRenderer:",c,"not supported, using",u,"instead."),c=u);const d=t.logarithmicDepthBuffer===!0,p=t.reversedDepthBuffer===!0&&e.has("EXT_clip_control"),f=n.getParameter(n.MAX_TEXTURE_IMAGE_UNITS),_=n.getParameter(n.MAX_VERTEX_TEXTURE_IMAGE_UNITS),g=n.getParameter(n.MAX_TEXTURE_SIZE),m=n.getParameter(n.MAX_CUBE_MAP_TEXTURE_SIZE),h=n.getParameter(n.MAX_VERTEX_ATTRIBS),v=n.getParameter(n.MAX_VERTEX_UNIFORM_VECTORS),x=n.getParameter(n.MAX_VARYING_VECTORS),w=n.getParameter(n.MAX_FRAGMENT_UNIFORM_VECTORS),S=_>0,C=n.getParameter(n.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:s,getMaxPrecision:l,textureFormatReadable:o,textureTypeReadable:a,precision:c,logarithmicDepthBuffer:d,reversedDepthBuffer:p,maxTextures:f,maxVertexTextures:_,maxTextureSize:g,maxCubemapSize:m,maxAttributes:h,maxVertexUniforms:v,maxVaryings:x,maxFragmentUniforms:w,vertexTextures:S,maxSamples:C}}function lM(n){const e=this;let t=null,i=0,r=!1,s=!1;const o=new Ci,a=new Fe,l={value:null,needsUpdate:!1};this.uniform=l,this.numPlanes=0,this.numIntersection=0,this.init=function(d,p){const f=d.length!==0||p||i!==0||r;return r=p,i=d.length,f},this.beginShadows=function(){s=!0,u(null)},this.endShadows=function(){s=!1},this.setGlobalState=function(d,p){t=u(d,p,0)},this.setState=function(d,p,f){const _=d.clippingPlanes,g=d.clipIntersection,m=d.clipShadows,h=n.get(d);if(!r||_===null||_.length===0||s&&!m)s?u(null):c();else{const v=s?0:i,x=v*4;let w=h.clippingState||null;l.value=w,w=u(_,p,x,f);for(let S=0;S!==x;++S)w[S]=t[S];h.clippingState=w,this.numIntersection=g?this.numPlanes:0,this.numPlanes+=v}};function c(){l.value!==t&&(l.value=t,l.needsUpdate=i>0),e.numPlanes=i,e.numIntersection=0}function u(d,p,f,_){const g=d!==null?d.length:0;let m=null;if(g!==0){if(m=l.value,_!==!0||m===null){const h=f+g*4,v=p.matrixWorldInverse;a.getNormalMatrix(v),(m===null||m.length<h)&&(m=new Float32Array(h));for(let x=0,w=f;x!==g;++x,w+=4)o.copy(d[x]).applyMatrix4(v,a),o.normal.toArray(m,w),m[w+3]=o.constant}l.value=m,l.needsUpdate=!0}return e.numPlanes=g,e.numIntersection=0,m}}function cM(n){let e=new WeakMap;function t(o,a){return a===vc?o.mapping=os:a===xc&&(o.mapping=as),o}function i(o){if(o&&o.isTexture){const a=o.mapping;if(a===vc||a===xc)if(e.has(o)){const l=e.get(o).texture;return t(l,o.mapping)}else{const l=o.image;if(l&&l.height>0){const c=new sb(l.height);return c.fromEquirectangularTexture(n,o),e.set(o,c),o.addEventListener("dispose",r),t(c.texture,o.mapping)}else return null}}return o}function r(o){const a=o.target;a.removeEventListener("dispose",r);const l=e.get(a);l!==void 0&&(e.delete(a),l.dispose())}function s(){e=new WeakMap}return{get:i,dispose:s}}const Xr=4,Eh=[.125,.215,.35,.446,.526,.582],ar=20,Ol=new xb,Mh=new Ze;let Fl=null,Nl=0,kl=0,Bl=!1;const ir=(1+Math.sqrt(5))/2,Vr=1/ir,Th=[new B(-ir,Vr,0),new B(ir,Vr,0),new B(-Vr,0,ir),new B(Vr,0,ir),new B(0,ir,-Vr),new B(0,ir,Vr),new B(-1,1,-1),new B(1,1,-1),new B(-1,1,1),new B(1,1,1)],uM=new B;class Ah{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,i=.1,r=100,s={}){const{size:o=256,position:a=uM}=s;Fl=this._renderer.getRenderTarget(),Nl=this._renderer.getActiveCubeFace(),kl=this._renderer.getActiveMipmapLevel(),Bl=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(o);const l=this._allocateTargets();return l.depthBuffer=!0,this._sceneToCubeUV(e,i,r,l,a),t>0&&this._blur(l,0,0,t),this._applyPMREM(l),this._cleanup(l),l}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=Rh(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=Ph(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(Fl,Nl,kl),this._renderer.xr.enabled=Bl,e.scissorTest=!1,qo(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===os||e.mapping===as?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),Fl=this._renderer.getRenderTarget(),Nl=this._renderer.getActiveCubeFace(),kl=this._renderer.getActiveMipmapLevel(),Bl=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const i=t||this._allocateTargets();return this._textureToCubeUV(e,i),this._applyPMREM(i),this._cleanup(i),i}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,i={magFilter:qn,minFilter:qn,generateMipmaps:!1,type:go,format:Nn,colorSpace:ls,depthBuffer:!1},r=Ch(e,t,i);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=Ch(e,t,i);const{_lodMax:s}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=dM(s)),this._blurMaterial=hM(s,e,t)}return r}_compileMaterial(e){const t=new jn(this._lodPlanes[0],e);this._renderer.compile(t,Ol)}_sceneToCubeUV(e,t,i,r,s){const l=new Cn(90,1,t,i),c=[1,-1,1,1,1,1],u=[1,1,1,-1,-1,-1],d=this._renderer,p=d.autoClear,f=d.toneMapping;d.getClearColor(Mh),d.toneMapping=Bi,d.autoClear=!1,d.state.buffers.depth.getReversed()&&(d.setRenderTarget(r),d.clearDepth(),d.setRenderTarget(null));const g=new tm({name:"PMREM.Background",side:qt,depthWrite:!1,depthTest:!1}),m=new jn(new Ss,g);let h=!1;const v=e.background;v?v.isColor&&(g.color.copy(v),e.background=null,h=!0):(g.color.copy(Mh),h=!0);for(let x=0;x<6;x++){const w=x%3;w===0?(l.up.set(0,c[x],0),l.position.set(s.x,s.y,s.z),l.lookAt(s.x+u[x],s.y,s.z)):w===1?(l.up.set(0,0,c[x]),l.position.set(s.x,s.y,s.z),l.lookAt(s.x,s.y+u[x],s.z)):(l.up.set(0,c[x],0),l.position.set(s.x,s.y,s.z),l.lookAt(s.x,s.y,s.z+u[x]));const S=this._cubeSize;qo(r,w*S,x>2?S:0,S,S),d.setRenderTarget(r),h&&d.render(m,l),d.render(e,l)}m.geometry.dispose(),m.material.dispose(),d.toneMapping=f,d.autoClear=p,e.background=v}_textureToCubeUV(e,t){const i=this._renderer,r=e.mapping===os||e.mapping===as;r?(this._cubemapMaterial===null&&(this._cubemapMaterial=Rh()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=Ph());const s=r?this._cubemapMaterial:this._equirectMaterial,o=new jn(this._lodPlanes[0],s),a=s.uniforms;a.envMap.value=e;const l=this._cubeSize;qo(t,0,0,3*l,2*l),i.setRenderTarget(t),i.render(o,Ol)}_applyPMREM(e){const t=this._renderer,i=t.autoClear;t.autoClear=!1;const r=this._lodPlanes.length;for(let s=1;s<r;s++){const o=Math.sqrt(this._sigmas[s]*this._sigmas[s]-this._sigmas[s-1]*this._sigmas[s-1]),a=Th[(r-s-1)%Th.length];this._blur(e,s-1,s,o,a)}t.autoClear=i}_blur(e,t,i,r,s){const o=this._pingPongRenderTarget;this._halfBlur(e,o,t,i,r,"latitudinal",s),this._halfBlur(o,e,i,i,r,"longitudinal",s)}_halfBlur(e,t,i,r,s,o,a){const l=this._renderer,c=this._blurMaterial;o!=="latitudinal"&&o!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const u=3,d=new jn(this._lodPlanes[r],c),p=c.uniforms,f=this._sizeLods[i]-1,_=isFinite(s)?Math.PI/(2*f):2*Math.PI/(2*ar-1),g=s/_,m=isFinite(s)?1+Math.floor(u*g):ar;m>ar&&console.warn(`sigmaRadians, ${s}, is too large and will clip, as it requested ${m} samples when the maximum is set to ${ar}`);const h=[];let v=0;for(let T=0;T<ar;++T){const A=T/g,b=Math.exp(-A*A/2);h.push(b),T===0?v+=b:T<m&&(v+=2*b)}for(let T=0;T<h.length;T++)h[T]=h[T]/v;p.envMap.value=e.texture,p.samples.value=m,p.weights.value=h,p.latitudinal.value=o==="latitudinal",a&&(p.poleAxis.value=a);const{_lodMax:x}=this;p.dTheta.value=_,p.mipInt.value=x-i;const w=this._sizeLods[r],S=3*w*(r>x-Xr?r-x+Xr:0),C=4*(this._cubeSize-w);qo(t,S,C,3*w,2*w),l.setRenderTarget(t),l.render(d,Ol)}}function dM(n){const e=[],t=[],i=[];let r=n;const s=n-Xr+1+Eh.length;for(let o=0;o<s;o++){const a=Math.pow(2,r);t.push(a);let l=1/a;o>n-Xr?l=Eh[o-n+Xr-1]:o===0&&(l=0),i.push(l);const c=1/(a-2),u=-c,d=1+c,p=[u,u,d,u,d,d,u,u,d,d,u,d],f=6,_=6,g=3,m=2,h=1,v=new Float32Array(g*_*f),x=new Float32Array(m*_*f),w=new Float32Array(h*_*f);for(let C=0;C<f;C++){const T=C%3*2/3-1,A=C>2?0:-1,b=[T,A,0,T+2/3,A,0,T+2/3,A+1,0,T,A,0,T+2/3,A+1,0,T,A+1,0];v.set(b,g*_*C),x.set(p,m*_*C);const y=[C,C,C,C,C,C];w.set(y,h*_*C)}const S=new yi;S.setAttribute("position",new Zn(v,g)),S.setAttribute("uv",new Zn(x,m)),S.setAttribute("faceIndex",new Zn(w,h)),e.push(S),r>Xr&&r--}return{lodPlanes:e,sizeLods:t,sigmas:i}}function Ch(n,e,t){const i=new xr(n,e,t);return i.texture.mapping=Ba,i.texture.name="PMREM.cubeUv",i.scissorTest=!0,i}function qo(n,e,t,i,r){n.viewport.set(e,t,i,r),n.scissor.set(e,t,i,r)}function hM(n,e,t){const i=new Float32Array(ar),r=new B(0,1,0);return new ti({name:"SphericalGaussianBlur",defines:{n:ar,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${n}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:i},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:r}},vertexShader:Ju(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform int samples;
			uniform float weights[ n ];
			uniform bool latitudinal;
			uniform float dTheta;
			uniform float mipInt;
			uniform vec3 poleAxis;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			vec3 getSample( float theta, vec3 axis ) {

				float cosTheta = cos( theta );
				// Rodrigues' axis-angle rotation
				vec3 sampleDirection = vOutputDirection * cosTheta
					+ cross( axis, vOutputDirection ) * sin( theta )
					+ axis * dot( axis, vOutputDirection ) * ( 1.0 - cosTheta );

				return bilinearCubeUV( envMap, sampleDirection, mipInt );

			}

			void main() {

				vec3 axis = latitudinal ? poleAxis : cross( poleAxis, vOutputDirection );

				if ( all( equal( axis, vec3( 0.0 ) ) ) ) {

					axis = vec3( vOutputDirection.z, 0.0, - vOutputDirection.x );

				}

				axis = normalize( axis );

				gl_FragColor = vec4( 0.0, 0.0, 0.0, 1.0 );
				gl_FragColor.rgb += weights[ 0 ] * getSample( 0.0, axis );

				for ( int i = 1; i < n; i++ ) {

					if ( i >= samples ) {

						break;

					}

					float theta = dTheta * float( i );
					gl_FragColor.rgb += weights[ i ] * getSample( -1.0 * theta, axis );
					gl_FragColor.rgb += weights[ i ] * getSample( theta, axis );

				}

			}
		`,blending:ki,depthTest:!1,depthWrite:!1})}function Ph(){return new ti({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:Ju(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;

			#include <common>

			void main() {

				vec3 outputDirection = normalize( vOutputDirection );
				vec2 uv = equirectUv( outputDirection );

				gl_FragColor = vec4( texture2D ( envMap, uv ).rgb, 1.0 );

			}
		`,blending:ki,depthTest:!1,depthWrite:!1})}function Rh(){return new ti({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Ju(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:ki,depthTest:!1,depthWrite:!1})}function Ju(){return`

		precision mediump float;
		precision mediump int;

		attribute float faceIndex;

		varying vec3 vOutputDirection;

		// RH coordinate system; PMREM face-indexing convention
		vec3 getDirection( vec2 uv, float face ) {

			uv = 2.0 * uv - 1.0;

			vec3 direction = vec3( uv, 1.0 );

			if ( face == 0.0 ) {

				direction = direction.zyx; // ( 1, v, u ) pos x

			} else if ( face == 1.0 ) {

				direction = direction.xzy;
				direction.xz *= -1.0; // ( -u, 1, -v ) pos y

			} else if ( face == 2.0 ) {

				direction.x *= -1.0; // ( -u, v, 1 ) pos z

			} else if ( face == 3.0 ) {

				direction = direction.zyx;
				direction.xz *= -1.0; // ( -1, v, -u ) neg x

			} else if ( face == 4.0 ) {

				direction = direction.xzy;
				direction.xy *= -1.0; // ( -u, -1, v ) neg y

			} else if ( face == 5.0 ) {

				direction.z *= -1.0; // ( u, v, -1 ) neg z

			}

			return direction;

		}

		void main() {

			vOutputDirection = getDirection( uv, faceIndex );
			gl_Position = vec4( position, 1.0 );

		}
	`}function fM(n){let e=new WeakMap,t=null;function i(a){if(a&&a.isTexture){const l=a.mapping,c=l===vc||l===xc,u=l===os||l===as;if(c||u){let d=e.get(a);const p=d!==void 0?d.texture.pmremVersion:0;if(a.isRenderTargetTexture&&a.pmremVersion!==p)return t===null&&(t=new Ah(n)),d=c?t.fromEquirectangular(a,d):t.fromCubemap(a,d),d.texture.pmremVersion=a.pmremVersion,e.set(a,d),d.texture;if(d!==void 0)return d.texture;{const f=a.image;return c&&f&&f.height>0||u&&f&&r(f)?(t===null&&(t=new Ah(n)),d=c?t.fromEquirectangular(a):t.fromCubemap(a),d.texture.pmremVersion=a.pmremVersion,e.set(a,d),a.addEventListener("dispose",s),d.texture):null}}}return a}function r(a){let l=0;const c=6;for(let u=0;u<c;u++)a[u]!==void 0&&l++;return l===c}function s(a){const l=a.target;l.removeEventListener("dispose",s);const c=e.get(l);c!==void 0&&(e.delete(l),c.dispose())}function o(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:i,dispose:o}}function pM(n){const e={};function t(i){if(e[i]!==void 0)return e[i];let r;switch(i){case"WEBGL_depth_texture":r=n.getExtension("WEBGL_depth_texture")||n.getExtension("MOZ_WEBGL_depth_texture")||n.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":r=n.getExtension("EXT_texture_filter_anisotropic")||n.getExtension("MOZ_EXT_texture_filter_anisotropic")||n.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":r=n.getExtension("WEBGL_compressed_texture_s3tc")||n.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||n.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":r=n.getExtension("WEBGL_compressed_texture_pvrtc")||n.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:r=n.getExtension(i)}return e[i]=r,r}return{has:function(i){return t(i)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(i){const r=t(i);return r===null&&Js("THREE.WebGLRenderer: "+i+" extension not supported."),r}}}function mM(n,e,t,i){const r={},s=new WeakMap;function o(d){const p=d.target;p.index!==null&&e.remove(p.index);for(const _ in p.attributes)e.remove(p.attributes[_]);p.removeEventListener("dispose",o),delete r[p.id];const f=s.get(p);f&&(e.remove(f),s.delete(p)),i.releaseStatesOfGeometry(p),p.isInstancedBufferGeometry===!0&&delete p._maxInstanceCount,t.memory.geometries--}function a(d,p){return r[p.id]===!0||(p.addEventListener("dispose",o),r[p.id]=!0,t.memory.geometries++),p}function l(d){const p=d.attributes;for(const f in p)e.update(p[f],n.ARRAY_BUFFER)}function c(d){const p=[],f=d.index,_=d.attributes.position;let g=0;if(f!==null){const v=f.array;g=f.version;for(let x=0,w=v.length;x<w;x+=3){const S=v[x+0],C=v[x+1],T=v[x+2];p.push(S,C,C,T,T,S)}}else if(_!==void 0){const v=_.array;g=_.version;for(let x=0,w=v.length/3-1;x<w;x+=3){const S=x+0,C=x+1,T=x+2;p.push(S,C,C,T,T,S)}}else return;const m=new(Zp(p)?im:nm)(p,1);m.version=g;const h=s.get(d);h&&e.remove(h),s.set(d,m)}function u(d){const p=s.get(d);if(p){const f=d.index;f!==null&&p.version<f.version&&c(d)}else c(d);return s.get(d)}return{get:a,update:l,getWireframeAttribute:u}}function gM(n,e,t){let i;function r(p){i=p}let s,o;function a(p){s=p.type,o=p.bytesPerElement}function l(p,f){n.drawElements(i,f,s,p*o),t.update(f,i,1)}function c(p,f,_){_!==0&&(n.drawElementsInstanced(i,f,s,p*o,_),t.update(f,i,_))}function u(p,f,_){if(_===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(i,f,0,s,p,0,_);let m=0;for(let h=0;h<_;h++)m+=f[h];t.update(m,i,1)}function d(p,f,_,g){if(_===0)return;const m=e.get("WEBGL_multi_draw");if(m===null)for(let h=0;h<p.length;h++)c(p[h]/o,f[h],g[h]);else{m.multiDrawElementsInstancedWEBGL(i,f,0,s,p,0,g,0,_);let h=0;for(let v=0;v<_;v++)h+=f[v]*g[v];t.update(h,i,1)}}this.setMode=r,this.setIndex=a,this.render=l,this.renderInstances=c,this.renderMultiDraw=u,this.renderMultiDrawInstances=d}function _M(n){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function i(s,o,a){switch(t.calls++,o){case n.TRIANGLES:t.triangles+=a*(s/3);break;case n.LINES:t.lines+=a*(s/2);break;case n.LINE_STRIP:t.lines+=a*(s-1);break;case n.LINE_LOOP:t.lines+=a*s;break;case n.POINTS:t.points+=a*s;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",o);break}}function r(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:r,update:i}}function vM(n,e,t){const i=new WeakMap,r=new yt;function s(o,a,l){const c=o.morphTargetInfluences,u=a.morphAttributes.position||a.morphAttributes.normal||a.morphAttributes.color,d=u!==void 0?u.length:0;let p=i.get(a);if(p===void 0||p.count!==d){let y=function(){A.dispose(),i.delete(a),a.removeEventListener("dispose",y)};var f=y;p!==void 0&&p.texture.dispose();const _=a.morphAttributes.position!==void 0,g=a.morphAttributes.normal!==void 0,m=a.morphAttributes.color!==void 0,h=a.morphAttributes.position||[],v=a.morphAttributes.normal||[],x=a.morphAttributes.color||[];let w=0;_===!0&&(w=1),g===!0&&(w=2),m===!0&&(w=3);let S=a.attributes.position.count*w,C=1;S>e.maxTextureSize&&(C=Math.ceil(S/e.maxTextureSize),S=e.maxTextureSize);const T=new Float32Array(S*C*4*d),A=new Jp(T,S,C,d);A.type=fi,A.needsUpdate=!0;const b=w*4;for(let P=0;P<d;P++){const D=h[P],O=v[P],V=x[P],k=S*C*4*P;for(let G=0;G<D.count;G++){const $=G*b;_===!0&&(r.fromBufferAttribute(D,G),T[k+$+0]=r.x,T[k+$+1]=r.y,T[k+$+2]=r.z,T[k+$+3]=0),g===!0&&(r.fromBufferAttribute(O,G),T[k+$+4]=r.x,T[k+$+5]=r.y,T[k+$+6]=r.z,T[k+$+7]=0),m===!0&&(r.fromBufferAttribute(V,G),T[k+$+8]=r.x,T[k+$+9]=r.y,T[k+$+10]=r.z,T[k+$+11]=V.itemSize===4?r.w:1)}}p={count:d,texture:A,size:new Be(S,C)},i.set(a,p),a.addEventListener("dispose",y)}if(o.isInstancedMesh===!0&&o.morphTexture!==null)l.getUniforms().setValue(n,"morphTexture",o.morphTexture,t);else{let _=0;for(let m=0;m<c.length;m++)_+=c[m];const g=a.morphTargetsRelative?1:1-_;l.getUniforms().setValue(n,"morphTargetBaseInfluence",g),l.getUniforms().setValue(n,"morphTargetInfluences",c)}l.getUniforms().setValue(n,"morphTargetsTexture",p.texture,t),l.getUniforms().setValue(n,"morphTargetsTextureSize",p.size)}return{update:s}}function xM(n,e,t,i){let r=new WeakMap;function s(l){const c=i.render.frame,u=l.geometry,d=e.get(l,u);if(r.get(d)!==c&&(e.update(d),r.set(d,c)),l.isInstancedMesh&&(l.hasEventListener("dispose",a)===!1&&l.addEventListener("dispose",a),r.get(l)!==c&&(t.update(l.instanceMatrix,n.ARRAY_BUFFER),l.instanceColor!==null&&t.update(l.instanceColor,n.ARRAY_BUFFER),r.set(l,c))),l.isSkinnedMesh){const p=l.skeleton;r.get(p)!==c&&(p.update(),r.set(p,c))}return d}function o(){r=new WeakMap}function a(l){const c=l.target;c.removeEventListener("dispose",a),t.remove(c.instanceMatrix),c.instanceColor!==null&&t.remove(c.instanceColor)}return{update:s,dispose:o}}const hm=new Yt,Dh=new cm(1,1),fm=new Jp,pm=new Gy,mm=new am,Lh=[],Ih=[],Uh=new Float32Array(16),Oh=new Float32Array(9),Fh=new Float32Array(4);function Es(n,e,t){const i=n[0];if(i<=0||i>0)return n;const r=e*t;let s=Lh[r];if(s===void 0&&(s=new Float32Array(r),Lh[r]=s),e!==0){i.toArray(s,0);for(let o=1,a=0;o!==e;++o)a+=t,n[o].toArray(s,a)}return s}function Pt(n,e){if(n.length!==e.length)return!1;for(let t=0,i=n.length;t<i;t++)if(n[t]!==e[t])return!1;return!0}function Rt(n,e){for(let t=0,i=e.length;t<i;t++)n[t]=e[t]}function Ha(n,e){let t=Ih[e];t===void 0&&(t=new Int32Array(e),Ih[e]=t);for(let i=0;i!==e;++i)t[i]=n.allocateTextureUnit();return t}function wM(n,e){const t=this.cache;t[0]!==e&&(n.uniform1f(this.addr,e),t[0]=e)}function yM(n,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(n.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Pt(t,e))return;n.uniform2fv(this.addr,e),Rt(t,e)}}function bM(n,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(n.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(n.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(Pt(t,e))return;n.uniform3fv(this.addr,e),Rt(t,e)}}function SM(n,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(n.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Pt(t,e))return;n.uniform4fv(this.addr,e),Rt(t,e)}}function EM(n,e){const t=this.cache,i=e.elements;if(i===void 0){if(Pt(t,e))return;n.uniformMatrix2fv(this.addr,!1,e),Rt(t,e)}else{if(Pt(t,i))return;Fh.set(i),n.uniformMatrix2fv(this.addr,!1,Fh),Rt(t,i)}}function MM(n,e){const t=this.cache,i=e.elements;if(i===void 0){if(Pt(t,e))return;n.uniformMatrix3fv(this.addr,!1,e),Rt(t,e)}else{if(Pt(t,i))return;Oh.set(i),n.uniformMatrix3fv(this.addr,!1,Oh),Rt(t,i)}}function TM(n,e){const t=this.cache,i=e.elements;if(i===void 0){if(Pt(t,e))return;n.uniformMatrix4fv(this.addr,!1,e),Rt(t,e)}else{if(Pt(t,i))return;Uh.set(i),n.uniformMatrix4fv(this.addr,!1,Uh),Rt(t,i)}}function AM(n,e){const t=this.cache;t[0]!==e&&(n.uniform1i(this.addr,e),t[0]=e)}function CM(n,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(n.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Pt(t,e))return;n.uniform2iv(this.addr,e),Rt(t,e)}}function PM(n,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(n.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(Pt(t,e))return;n.uniform3iv(this.addr,e),Rt(t,e)}}function RM(n,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(n.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Pt(t,e))return;n.uniform4iv(this.addr,e),Rt(t,e)}}function DM(n,e){const t=this.cache;t[0]!==e&&(n.uniform1ui(this.addr,e),t[0]=e)}function LM(n,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(n.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Pt(t,e))return;n.uniform2uiv(this.addr,e),Rt(t,e)}}function IM(n,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(n.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(Pt(t,e))return;n.uniform3uiv(this.addr,e),Rt(t,e)}}function UM(n,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(n.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Pt(t,e))return;n.uniform4uiv(this.addr,e),Rt(t,e)}}function OM(n,e,t){const i=this.cache,r=t.allocateTextureUnit();i[0]!==r&&(n.uniform1i(this.addr,r),i[0]=r);let s;this.type===n.SAMPLER_2D_SHADOW?(Dh.compareFunction=Kp,s=Dh):s=hm,t.setTexture2D(e||s,r)}function FM(n,e,t){const i=this.cache,r=t.allocateTextureUnit();i[0]!==r&&(n.uniform1i(this.addr,r),i[0]=r),t.setTexture3D(e||pm,r)}function NM(n,e,t){const i=this.cache,r=t.allocateTextureUnit();i[0]!==r&&(n.uniform1i(this.addr,r),i[0]=r),t.setTextureCube(e||mm,r)}function kM(n,e,t){const i=this.cache,r=t.allocateTextureUnit();i[0]!==r&&(n.uniform1i(this.addr,r),i[0]=r),t.setTexture2DArray(e||fm,r)}function BM(n){switch(n){case 5126:return wM;case 35664:return yM;case 35665:return bM;case 35666:return SM;case 35674:return EM;case 35675:return MM;case 35676:return TM;case 5124:case 35670:return AM;case 35667:case 35671:return CM;case 35668:case 35672:return PM;case 35669:case 35673:return RM;case 5125:return DM;case 36294:return LM;case 36295:return IM;case 36296:return UM;case 35678:case 36198:case 36298:case 36306:case 35682:return OM;case 35679:case 36299:case 36307:return FM;case 35680:case 36300:case 36308:case 36293:return NM;case 36289:case 36303:case 36311:case 36292:return kM}}function zM(n,e){n.uniform1fv(this.addr,e)}function VM(n,e){const t=Es(e,this.size,2);n.uniform2fv(this.addr,t)}function HM(n,e){const t=Es(e,this.size,3);n.uniform3fv(this.addr,t)}function GM(n,e){const t=Es(e,this.size,4);n.uniform4fv(this.addr,t)}function WM(n,e){const t=Es(e,this.size,4);n.uniformMatrix2fv(this.addr,!1,t)}function XM(n,e){const t=Es(e,this.size,9);n.uniformMatrix3fv(this.addr,!1,t)}function $M(n,e){const t=Es(e,this.size,16);n.uniformMatrix4fv(this.addr,!1,t)}function qM(n,e){n.uniform1iv(this.addr,e)}function YM(n,e){n.uniform2iv(this.addr,e)}function jM(n,e){n.uniform3iv(this.addr,e)}function KM(n,e){n.uniform4iv(this.addr,e)}function ZM(n,e){n.uniform1uiv(this.addr,e)}function JM(n,e){n.uniform2uiv(this.addr,e)}function QM(n,e){n.uniform3uiv(this.addr,e)}function eT(n,e){n.uniform4uiv(this.addr,e)}function tT(n,e,t){const i=this.cache,r=e.length,s=Ha(t,r);Pt(i,s)||(n.uniform1iv(this.addr,s),Rt(i,s));for(let o=0;o!==r;++o)t.setTexture2D(e[o]||hm,s[o])}function nT(n,e,t){const i=this.cache,r=e.length,s=Ha(t,r);Pt(i,s)||(n.uniform1iv(this.addr,s),Rt(i,s));for(let o=0;o!==r;++o)t.setTexture3D(e[o]||pm,s[o])}function iT(n,e,t){const i=this.cache,r=e.length,s=Ha(t,r);Pt(i,s)||(n.uniform1iv(this.addr,s),Rt(i,s));for(let o=0;o!==r;++o)t.setTextureCube(e[o]||mm,s[o])}function rT(n,e,t){const i=this.cache,r=e.length,s=Ha(t,r);Pt(i,s)||(n.uniform1iv(this.addr,s),Rt(i,s));for(let o=0;o!==r;++o)t.setTexture2DArray(e[o]||fm,s[o])}function sT(n){switch(n){case 5126:return zM;case 35664:return VM;case 35665:return HM;case 35666:return GM;case 35674:return WM;case 35675:return XM;case 35676:return $M;case 5124:case 35670:return qM;case 35667:case 35671:return YM;case 35668:case 35672:return jM;case 35669:case 35673:return KM;case 5125:return ZM;case 36294:return JM;case 36295:return QM;case 36296:return eT;case 35678:case 36198:case 36298:case 36306:case 35682:return tT;case 35679:case 36299:case 36307:return nT;case 35680:case 36300:case 36308:case 36293:return iT;case 36289:case 36303:case 36311:case 36292:return rT}}class oT{constructor(e,t,i){this.id=e,this.addr=i,this.cache=[],this.type=t.type,this.setValue=BM(t.type)}}class aT{constructor(e,t,i){this.id=e,this.addr=i,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=sT(t.type)}}class lT{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,i){const r=this.seq;for(let s=0,o=r.length;s!==o;++s){const a=r[s];a.setValue(e,t[a.id],i)}}}const zl=/(\w+)(\])?(\[|\.)?/g;function Nh(n,e){n.seq.push(e),n.map[e.id]=e}function cT(n,e,t){const i=n.name,r=i.length;for(zl.lastIndex=0;;){const s=zl.exec(i),o=zl.lastIndex;let a=s[1];const l=s[2]==="]",c=s[3];if(l&&(a=a|0),c===void 0||c==="["&&o+2===r){Nh(t,c===void 0?new oT(a,n,e):new aT(a,n,e));break}else{let d=t.map[a];d===void 0&&(d=new lT(a),Nh(t,d)),t=d}}}class ia{constructor(e,t){this.seq=[],this.map={};const i=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let r=0;r<i;++r){const s=e.getActiveUniform(t,r),o=e.getUniformLocation(t,s.name);cT(s,o,this)}}setValue(e,t,i,r){const s=this.map[t];s!==void 0&&s.setValue(e,i,r)}setOptional(e,t,i){const r=t[i];r!==void 0&&this.setValue(e,i,r)}static upload(e,t,i,r){for(let s=0,o=t.length;s!==o;++s){const a=t[s],l=i[a.id];l.needsUpdate!==!1&&a.setValue(e,l.value,r)}}static seqWithValue(e,t){const i=[];for(let r=0,s=e.length;r!==s;++r){const o=e[r];o.id in t&&i.push(o)}return i}}function kh(n,e,t){const i=n.createShader(e);return n.shaderSource(i,t),n.compileShader(i),i}const uT=37297;let dT=0;function hT(n,e){const t=n.split(`
`),i=[],r=Math.max(e-6,0),s=Math.min(e+6,t.length);for(let o=r;o<s;o++){const a=o+1;i.push(`${a===e?">":" "} ${a}: ${t[o]}`)}return i.join(`
`)}const Bh=new Fe;function fT(n){qe._getMatrix(Bh,qe.workingColorSpace,n);const e=`mat3( ${Bh.elements.map(t=>t.toFixed(4))} )`;switch(qe.getTransfer(n)){case ba:return[e,"LinearTransferOETF"];case et:return[e,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space: ",n),[e,"LinearTransferOETF"]}}function zh(n,e,t){const i=n.getShaderParameter(e,n.COMPILE_STATUS),s=(n.getShaderInfoLog(e)||"").trim();if(i&&s==="")return"";const o=/ERROR: 0:(\d+)/.exec(s);if(o){const a=parseInt(o[1]);return t.toUpperCase()+`

`+s+`

`+hT(n.getShaderSource(e),a)}else return s}function pT(n,e){const t=fT(e);return[`vec4 ${n}( vec4 value ) {`,`	return ${t[1]}( vec4( value.rgb * ${t[0]}, value.a ) );`,"}"].join(`
`)}function mT(n,e){let t;switch(e){case ty:t="Linear";break;case ny:t="Reinhard";break;case iy:t="Cineon";break;case ry:t="ACESFilmic";break;case oy:t="AgX";break;case ay:t="Neutral";break;case sy:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+n+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const Yo=new B;function gT(){qe.getLuminanceCoefficients(Yo);const n=Yo.x.toFixed(4),e=Yo.y.toFixed(4),t=Yo.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${n}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function _T(n){return[n.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",n.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(Ls).join(`
`)}function vT(n){const e=[];for(const t in n){const i=n[t];i!==!1&&e.push("#define "+t+" "+i)}return e.join(`
`)}function xT(n,e){const t={},i=n.getProgramParameter(e,n.ACTIVE_ATTRIBUTES);for(let r=0;r<i;r++){const s=n.getActiveAttrib(e,r),o=s.name;let a=1;s.type===n.FLOAT_MAT2&&(a=2),s.type===n.FLOAT_MAT3&&(a=3),s.type===n.FLOAT_MAT4&&(a=4),t[o]={type:s.type,location:n.getAttribLocation(e,o),locationSize:a}}return t}function Ls(n){return n!==""}function Vh(n,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return n.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function Hh(n,e){return n.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const wT=/^[ \t]*#include +<([\w\d./]+)>/gm;function Qc(n){return n.replace(wT,bT)}const yT=new Map;function bT(n,e){let t=ke[e];if(t===void 0){const i=yT.get(e);if(i!==void 0)t=ke[i],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,i);else throw new Error("Can not resolve #include <"+e+">")}return Qc(t)}const ST=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function Gh(n){return n.replace(ST,ET)}function ET(n,e,t,i){let r="";for(let s=parseInt(e);s<parseInt(t);s++)r+=i.replace(/\[\s*i\s*\]/g,"[ "+s+" ]").replace(/UNROLLED_LOOP_INDEX/g,s);return r}function Wh(n){let e=`precision ${n.precision} float;
	precision ${n.precision} int;
	precision ${n.precision} sampler2D;
	precision ${n.precision} samplerCube;
	precision ${n.precision} sampler3D;
	precision ${n.precision} sampler2DArray;
	precision ${n.precision} sampler2DShadow;
	precision ${n.precision} samplerCubeShadow;
	precision ${n.precision} sampler2DArrayShadow;
	precision ${n.precision} isampler2D;
	precision ${n.precision} isampler3D;
	precision ${n.precision} isamplerCube;
	precision ${n.precision} isampler2DArray;
	precision ${n.precision} usampler2D;
	precision ${n.precision} usampler3D;
	precision ${n.precision} usamplerCube;
	precision ${n.precision} usampler2DArray;
	`;return n.precision==="highp"?e+=`
#define HIGH_PRECISION`:n.precision==="mediump"?e+=`
#define MEDIUM_PRECISION`:n.precision==="lowp"&&(e+=`
#define LOW_PRECISION`),e}function MT(n){let e="SHADOWMAP_TYPE_BASIC";return n.shadowMapType===Bp?e="SHADOWMAP_TYPE_PCF":n.shadowMapType===Uw?e="SHADOWMAP_TYPE_PCF_SOFT":n.shadowMapType===ci&&(e="SHADOWMAP_TYPE_VSM"),e}function TT(n){let e="ENVMAP_TYPE_CUBE";if(n.envMap)switch(n.envMapMode){case os:case as:e="ENVMAP_TYPE_CUBE";break;case Ba:e="ENVMAP_TYPE_CUBE_UV";break}return e}function AT(n){let e="ENVMAP_MODE_REFLECTION";if(n.envMap)switch(n.envMapMode){case as:e="ENVMAP_MODE_REFRACTION";break}return e}function CT(n){let e="ENVMAP_BLENDING_NONE";if(n.envMap)switch(n.combine){case zp:e="ENVMAP_BLENDING_MULTIPLY";break;case Qw:e="ENVMAP_BLENDING_MIX";break;case ey:e="ENVMAP_BLENDING_ADD";break}return e}function PT(n){const e=n.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,i=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),112)),texelHeight:i,maxMip:t}}function RT(n,e,t,i){const r=n.getContext(),s=t.defines;let o=t.vertexShader,a=t.fragmentShader;const l=MT(t),c=TT(t),u=AT(t),d=CT(t),p=PT(t),f=_T(t),_=vT(s),g=r.createProgram();let m,h,v=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(m=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,_].filter(Ls).join(`
`),m.length>0&&(m+=`
`),h=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,_].filter(Ls).join(`
`),h.length>0&&(h+=`
`)):(m=[Wh(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,_,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+u:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGARITHMIC_DEPTH_BUFFER":"",t.reversedDepthBuffer?"#define USE_REVERSED_DEPTH_BUFFER":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(Ls).join(`
`),h=[Wh(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,_,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+c:"",t.envMap?"#define "+u:"",t.envMap?"#define "+d:"",p?"#define CUBEUV_TEXEL_WIDTH "+p.texelWidth:"",p?"#define CUBEUV_TEXEL_HEIGHT "+p.texelHeight:"",p?"#define CUBEUV_MAX_MIP "+p.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",t.logarithmicDepthBuffer?"#define USE_LOGARITHMIC_DEPTH_BUFFER":"",t.reversedDepthBuffer?"#define USE_REVERSED_DEPTH_BUFFER":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==Bi?"#define TONE_MAPPING":"",t.toneMapping!==Bi?ke.tonemapping_pars_fragment:"",t.toneMapping!==Bi?mT("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",ke.colorspace_pars_fragment,pT("linearToOutputTexel",t.outputColorSpace),gT(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(Ls).join(`
`)),o=Qc(o),o=Vh(o,t),o=Hh(o,t),a=Qc(a),a=Vh(a,t),a=Hh(a,t),o=Gh(o),a=Gh(a),t.isRawShaderMaterial!==!0&&(v=`#version 300 es
`,m=[f,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+m,h=["#define varying in",t.glslVersion===nh?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===nh?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+h);const x=v+m+o,w=v+h+a,S=kh(r,r.VERTEX_SHADER,x),C=kh(r,r.FRAGMENT_SHADER,w);r.attachShader(g,S),r.attachShader(g,C),t.index0AttributeName!==void 0?r.bindAttribLocation(g,0,t.index0AttributeName):t.morphTargets===!0&&r.bindAttribLocation(g,0,"position"),r.linkProgram(g);function T(P){if(n.debug.checkShaderErrors){const D=r.getProgramInfoLog(g)||"",O=r.getShaderInfoLog(S)||"",V=r.getShaderInfoLog(C)||"",k=D.trim(),G=O.trim(),$=V.trim();let U=!0,Z=!0;if(r.getProgramParameter(g,r.LINK_STATUS)===!1)if(U=!1,typeof n.debug.onShaderError=="function")n.debug.onShaderError(r,g,S,C);else{const ee=zh(r,S,"vertex"),ce=zh(r,C,"fragment");console.error("THREE.WebGLProgram: Shader Error "+r.getError()+" - VALIDATE_STATUS "+r.getProgramParameter(g,r.VALIDATE_STATUS)+`

Material Name: `+P.name+`
Material Type: `+P.type+`

Program Info Log: `+k+`
`+ee+`
`+ce)}else k!==""?console.warn("THREE.WebGLProgram: Program Info Log:",k):(G===""||$==="")&&(Z=!1);Z&&(P.diagnostics={runnable:U,programLog:k,vertexShader:{log:G,prefix:m},fragmentShader:{log:$,prefix:h}})}r.deleteShader(S),r.deleteShader(C),A=new ia(r,g),b=xT(r,g)}let A;this.getUniforms=function(){return A===void 0&&T(this),A};let b;this.getAttributes=function(){return b===void 0&&T(this),b};let y=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return y===!1&&(y=r.getProgramParameter(g,uT)),y},this.destroy=function(){i.releaseStatesOfProgram(this),r.deleteProgram(g),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=dT++,this.cacheKey=e,this.usedTimes=1,this.program=g,this.vertexShader=S,this.fragmentShader=C,this}let DT=0;class LT{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,i=e.fragmentShader,r=this._getShaderStage(t),s=this._getShaderStage(i),o=this._getShaderCacheForMaterial(e);return o.has(r)===!1&&(o.add(r),r.usedTimes++),o.has(s)===!1&&(o.add(s),s.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const i of t)i.usedTimes--,i.usedTimes===0&&this.shaderCache.delete(i.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let i=t.get(e);return i===void 0&&(i=new Set,t.set(e,i)),i}_getShaderStage(e){const t=this.shaderCache;let i=t.get(e);return i===void 0&&(i=new IT(e),t.set(e,i)),i}}class IT{constructor(e){this.id=DT++,this.code=e,this.usedTimes=0}}function UT(n,e,t,i,r,s,o){const a=new Qp,l=new LT,c=new Set,u=[],d=r.logarithmicDepthBuffer,p=r.vertexTextures;let f=r.precision;const _={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function g(b){return c.add(b),b===0?"uv":`uv${b}`}function m(b,y,P,D,O){const V=D.fog,k=O.geometry,G=b.isMeshStandardMaterial?D.environment:null,$=(b.isMeshStandardMaterial?t:e).get(b.envMap||G),U=$&&$.mapping===Ba?$.image.height:null,Z=_[b.type];b.precision!==null&&(f=r.getMaxPrecision(b.precision),f!==b.precision&&console.warn("THREE.WebGLProgram.getParameters:",b.precision,"not supported, using",f,"instead."));const ee=k.morphAttributes.position||k.morphAttributes.normal||k.morphAttributes.color,ce=ee!==void 0?ee.length:0;let Ae=0;k.morphAttributes.position!==void 0&&(Ae=1),k.morphAttributes.normal!==void 0&&(Ae=2),k.morphAttributes.color!==void 0&&(Ae=3);let Je,We,ze,j;if(Z){const Ke=Gn[Z];Je=Ke.vertexShader,We=Ke.fragmentShader}else Je=b.vertexShader,We=b.fragmentShader,l.update(b),ze=l.getVertexShaderID(b),j=l.getFragmentShaderID(b);const Q=n.getRenderTarget(),pe=n.state.buffers.depth.getReversed(),Le=O.isInstancedMesh===!0,Se=O.isBatchedMesh===!0,Xe=!!b.map,Nt=!!b.matcap,L=!!$,ct=!!b.aoMap,Ue=!!b.lightMap,Re=!!b.bumpMap,_e=!!b.normalMap,ut=!!b.displacementMap,ve=!!b.emissiveMap,Ne=!!b.metalnessMap,Dt=!!b.roughnessMap,vt=b.anisotropy>0,R=b.clearcoat>0,E=b.dispersion>0,z=b.iridescence>0,Y=b.sheen>0,J=b.transmission>0,q=vt&&!!b.anisotropyMap,be=R&&!!b.clearcoatMap,se=R&&!!b.clearcoatNormalMap,xe=R&&!!b.clearcoatRoughnessMap,we=z&&!!b.iridescenceMap,ie=z&&!!b.iridescenceThicknessMap,de=Y&&!!b.sheenColorMap,Pe=Y&&!!b.sheenRoughnessMap,ye=!!b.specularMap,le=!!b.specularColorMap,Oe=!!b.specularIntensityMap,I=J&&!!b.transmissionMap,re=J&&!!b.thicknessMap,oe=!!b.gradientMap,fe=!!b.alphaMap,te=b.alphaTest>0,K=!!b.alphaHash,ge=!!b.extensions;let Ie=Bi;b.toneMapped&&(Q===null||Q.isXRRenderTarget===!0)&&(Ie=n.toneMapping);const st={shaderID:Z,shaderType:b.type,shaderName:b.name,vertexShader:Je,fragmentShader:We,defines:b.defines,customVertexShaderID:ze,customFragmentShaderID:j,isRawShaderMaterial:b.isRawShaderMaterial===!0,glslVersion:b.glslVersion,precision:f,batching:Se,batchingColor:Se&&O._colorsTexture!==null,instancing:Le,instancingColor:Le&&O.instanceColor!==null,instancingMorph:Le&&O.morphTexture!==null,supportsVertexTextures:p,outputColorSpace:Q===null?n.outputColorSpace:Q.isXRRenderTarget===!0?Q.texture.colorSpace:ls,alphaToCoverage:!!b.alphaToCoverage,map:Xe,matcap:Nt,envMap:L,envMapMode:L&&$.mapping,envMapCubeUVHeight:U,aoMap:ct,lightMap:Ue,bumpMap:Re,normalMap:_e,displacementMap:p&&ut,emissiveMap:ve,normalMapObjectSpace:_e&&b.normalMapType===hy,normalMapTangentSpace:_e&&b.normalMapType===dy,metalnessMap:Ne,roughnessMap:Dt,anisotropy:vt,anisotropyMap:q,clearcoat:R,clearcoatMap:be,clearcoatNormalMap:se,clearcoatRoughnessMap:xe,dispersion:E,iridescence:z,iridescenceMap:we,iridescenceThicknessMap:ie,sheen:Y,sheenColorMap:de,sheenRoughnessMap:Pe,specularMap:ye,specularColorMap:le,specularIntensityMap:Oe,transmission:J,transmissionMap:I,thicknessMap:re,gradientMap:oe,opaque:b.transparent===!1&&b.blending===Zr&&b.alphaToCoverage===!1,alphaMap:fe,alphaTest:te,alphaHash:K,combine:b.combine,mapUv:Xe&&g(b.map.channel),aoMapUv:ct&&g(b.aoMap.channel),lightMapUv:Ue&&g(b.lightMap.channel),bumpMapUv:Re&&g(b.bumpMap.channel),normalMapUv:_e&&g(b.normalMap.channel),displacementMapUv:ut&&g(b.displacementMap.channel),emissiveMapUv:ve&&g(b.emissiveMap.channel),metalnessMapUv:Ne&&g(b.metalnessMap.channel),roughnessMapUv:Dt&&g(b.roughnessMap.channel),anisotropyMapUv:q&&g(b.anisotropyMap.channel),clearcoatMapUv:be&&g(b.clearcoatMap.channel),clearcoatNormalMapUv:se&&g(b.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:xe&&g(b.clearcoatRoughnessMap.channel),iridescenceMapUv:we&&g(b.iridescenceMap.channel),iridescenceThicknessMapUv:ie&&g(b.iridescenceThicknessMap.channel),sheenColorMapUv:de&&g(b.sheenColorMap.channel),sheenRoughnessMapUv:Pe&&g(b.sheenRoughnessMap.channel),specularMapUv:ye&&g(b.specularMap.channel),specularColorMapUv:le&&g(b.specularColorMap.channel),specularIntensityMapUv:Oe&&g(b.specularIntensityMap.channel),transmissionMapUv:I&&g(b.transmissionMap.channel),thicknessMapUv:re&&g(b.thicknessMap.channel),alphaMapUv:fe&&g(b.alphaMap.channel),vertexTangents:!!k.attributes.tangent&&(_e||vt),vertexColors:b.vertexColors,vertexAlphas:b.vertexColors===!0&&!!k.attributes.color&&k.attributes.color.itemSize===4,pointsUvs:O.isPoints===!0&&!!k.attributes.uv&&(Xe||fe),fog:!!V,useFog:b.fog===!0,fogExp2:!!V&&V.isFogExp2,flatShading:b.flatShading===!0&&b.wireframe===!1,sizeAttenuation:b.sizeAttenuation===!0,logarithmicDepthBuffer:d,reversedDepthBuffer:pe,skinning:O.isSkinnedMesh===!0,morphTargets:k.morphAttributes.position!==void 0,morphNormals:k.morphAttributes.normal!==void 0,morphColors:k.morphAttributes.color!==void 0,morphTargetsCount:ce,morphTextureStride:Ae,numDirLights:y.directional.length,numPointLights:y.point.length,numSpotLights:y.spot.length,numSpotLightMaps:y.spotLightMap.length,numRectAreaLights:y.rectArea.length,numHemiLights:y.hemi.length,numDirLightShadows:y.directionalShadowMap.length,numPointLightShadows:y.pointShadowMap.length,numSpotLightShadows:y.spotShadowMap.length,numSpotLightShadowsWithMaps:y.numSpotLightShadowsWithMaps,numLightProbes:y.numLightProbes,numClippingPlanes:o.numPlanes,numClipIntersection:o.numIntersection,dithering:b.dithering,shadowMapEnabled:n.shadowMap.enabled&&P.length>0,shadowMapType:n.shadowMap.type,toneMapping:Ie,decodeVideoTexture:Xe&&b.map.isVideoTexture===!0&&qe.getTransfer(b.map.colorSpace)===et,decodeVideoTextureEmissive:ve&&b.emissiveMap.isVideoTexture===!0&&qe.getTransfer(b.emissiveMap.colorSpace)===et,premultipliedAlpha:b.premultipliedAlpha,doubleSided:b.side===hi,flipSided:b.side===qt,useDepthPacking:b.depthPacking>=0,depthPacking:b.depthPacking||0,index0AttributeName:b.index0AttributeName,extensionClipCullDistance:ge&&b.extensions.clipCullDistance===!0&&i.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(ge&&b.extensions.multiDraw===!0||Se)&&i.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:i.has("KHR_parallel_shader_compile"),customProgramCacheKey:b.customProgramCacheKey()};return st.vertexUv1s=c.has(1),st.vertexUv2s=c.has(2),st.vertexUv3s=c.has(3),c.clear(),st}function h(b){const y=[];if(b.shaderID?y.push(b.shaderID):(y.push(b.customVertexShaderID),y.push(b.customFragmentShaderID)),b.defines!==void 0)for(const P in b.defines)y.push(P),y.push(b.defines[P]);return b.isRawShaderMaterial===!1&&(v(y,b),x(y,b),y.push(n.outputColorSpace)),y.push(b.customProgramCacheKey),y.join()}function v(b,y){b.push(y.precision),b.push(y.outputColorSpace),b.push(y.envMapMode),b.push(y.envMapCubeUVHeight),b.push(y.mapUv),b.push(y.alphaMapUv),b.push(y.lightMapUv),b.push(y.aoMapUv),b.push(y.bumpMapUv),b.push(y.normalMapUv),b.push(y.displacementMapUv),b.push(y.emissiveMapUv),b.push(y.metalnessMapUv),b.push(y.roughnessMapUv),b.push(y.anisotropyMapUv),b.push(y.clearcoatMapUv),b.push(y.clearcoatNormalMapUv),b.push(y.clearcoatRoughnessMapUv),b.push(y.iridescenceMapUv),b.push(y.iridescenceThicknessMapUv),b.push(y.sheenColorMapUv),b.push(y.sheenRoughnessMapUv),b.push(y.specularMapUv),b.push(y.specularColorMapUv),b.push(y.specularIntensityMapUv),b.push(y.transmissionMapUv),b.push(y.thicknessMapUv),b.push(y.combine),b.push(y.fogExp2),b.push(y.sizeAttenuation),b.push(y.morphTargetsCount),b.push(y.morphAttributeCount),b.push(y.numDirLights),b.push(y.numPointLights),b.push(y.numSpotLights),b.push(y.numSpotLightMaps),b.push(y.numHemiLights),b.push(y.numRectAreaLights),b.push(y.numDirLightShadows),b.push(y.numPointLightShadows),b.push(y.numSpotLightShadows),b.push(y.numSpotLightShadowsWithMaps),b.push(y.numLightProbes),b.push(y.shadowMapType),b.push(y.toneMapping),b.push(y.numClippingPlanes),b.push(y.numClipIntersection),b.push(y.depthPacking)}function x(b,y){a.disableAll(),y.supportsVertexTextures&&a.enable(0),y.instancing&&a.enable(1),y.instancingColor&&a.enable(2),y.instancingMorph&&a.enable(3),y.matcap&&a.enable(4),y.envMap&&a.enable(5),y.normalMapObjectSpace&&a.enable(6),y.normalMapTangentSpace&&a.enable(7),y.clearcoat&&a.enable(8),y.iridescence&&a.enable(9),y.alphaTest&&a.enable(10),y.vertexColors&&a.enable(11),y.vertexAlphas&&a.enable(12),y.vertexUv1s&&a.enable(13),y.vertexUv2s&&a.enable(14),y.vertexUv3s&&a.enable(15),y.vertexTangents&&a.enable(16),y.anisotropy&&a.enable(17),y.alphaHash&&a.enable(18),y.batching&&a.enable(19),y.dispersion&&a.enable(20),y.batchingColor&&a.enable(21),y.gradientMap&&a.enable(22),b.push(a.mask),a.disableAll(),y.fog&&a.enable(0),y.useFog&&a.enable(1),y.flatShading&&a.enable(2),y.logarithmicDepthBuffer&&a.enable(3),y.reversedDepthBuffer&&a.enable(4),y.skinning&&a.enable(5),y.morphTargets&&a.enable(6),y.morphNormals&&a.enable(7),y.morphColors&&a.enable(8),y.premultipliedAlpha&&a.enable(9),y.shadowMapEnabled&&a.enable(10),y.doubleSided&&a.enable(11),y.flipSided&&a.enable(12),y.useDepthPacking&&a.enable(13),y.dithering&&a.enable(14),y.transmission&&a.enable(15),y.sheen&&a.enable(16),y.opaque&&a.enable(17),y.pointsUvs&&a.enable(18),y.decodeVideoTexture&&a.enable(19),y.decodeVideoTextureEmissive&&a.enable(20),y.alphaToCoverage&&a.enable(21),b.push(a.mask)}function w(b){const y=_[b.type];let P;if(y){const D=Gn[y];P=sm.clone(D.uniforms)}else P=b.uniforms;return P}function S(b,y){let P;for(let D=0,O=u.length;D<O;D++){const V=u[D];if(V.cacheKey===y){P=V,++P.usedTimes;break}}return P===void 0&&(P=new RT(n,y,b,s),u.push(P)),P}function C(b){if(--b.usedTimes===0){const y=u.indexOf(b);u[y]=u[u.length-1],u.pop(),b.destroy()}}function T(b){l.remove(b)}function A(){l.dispose()}return{getParameters:m,getProgramCacheKey:h,getUniforms:w,acquireProgram:S,releaseProgram:C,releaseShaderCache:T,programs:u,dispose:A}}function OT(){let n=new WeakMap;function e(o){return n.has(o)}function t(o){let a=n.get(o);return a===void 0&&(a={},n.set(o,a)),a}function i(o){n.delete(o)}function r(o,a,l){n.get(o)[a]=l}function s(){n=new WeakMap}return{has:e,get:t,remove:i,update:r,dispose:s}}function FT(n,e){return n.groupOrder!==e.groupOrder?n.groupOrder-e.groupOrder:n.renderOrder!==e.renderOrder?n.renderOrder-e.renderOrder:n.material.id!==e.material.id?n.material.id-e.material.id:n.z!==e.z?n.z-e.z:n.id-e.id}function Xh(n,e){return n.groupOrder!==e.groupOrder?n.groupOrder-e.groupOrder:n.renderOrder!==e.renderOrder?n.renderOrder-e.renderOrder:n.z!==e.z?e.z-n.z:n.id-e.id}function $h(){const n=[];let e=0;const t=[],i=[],r=[];function s(){e=0,t.length=0,i.length=0,r.length=0}function o(d,p,f,_,g,m){let h=n[e];return h===void 0?(h={id:d.id,object:d,geometry:p,material:f,groupOrder:_,renderOrder:d.renderOrder,z:g,group:m},n[e]=h):(h.id=d.id,h.object=d,h.geometry=p,h.material=f,h.groupOrder=_,h.renderOrder=d.renderOrder,h.z=g,h.group=m),e++,h}function a(d,p,f,_,g,m){const h=o(d,p,f,_,g,m);f.transmission>0?i.push(h):f.transparent===!0?r.push(h):t.push(h)}function l(d,p,f,_,g,m){const h=o(d,p,f,_,g,m);f.transmission>0?i.unshift(h):f.transparent===!0?r.unshift(h):t.unshift(h)}function c(d,p){t.length>1&&t.sort(d||FT),i.length>1&&i.sort(p||Xh),r.length>1&&r.sort(p||Xh)}function u(){for(let d=e,p=n.length;d<p;d++){const f=n[d];if(f.id===null)break;f.id=null,f.object=null,f.geometry=null,f.material=null,f.group=null}}return{opaque:t,transmissive:i,transparent:r,init:s,push:a,unshift:l,finish:u,sort:c}}function NT(){let n=new WeakMap;function e(i,r){const s=n.get(i);let o;return s===void 0?(o=new $h,n.set(i,[o])):r>=s.length?(o=new $h,s.push(o)):o=s[r],o}function t(){n=new WeakMap}return{get:e,dispose:t}}function kT(){const n={};return{get:function(e){if(n[e.id]!==void 0)return n[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new B,color:new Ze};break;case"SpotLight":t={position:new B,direction:new B,color:new Ze,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new B,color:new Ze,distance:0,decay:0};break;case"HemisphereLight":t={direction:new B,skyColor:new Ze,groundColor:new Ze};break;case"RectAreaLight":t={color:new Ze,position:new B,halfWidth:new B,halfHeight:new B};break}return n[e.id]=t,t}}}function BT(){const n={};return{get:function(e){if(n[e.id]!==void 0)return n[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Be};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Be};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Be,shadowCameraNear:1,shadowCameraFar:1e3};break}return n[e.id]=t,t}}}let zT=0;function VT(n,e){return(e.castShadow?2:0)-(n.castShadow?2:0)+(e.map?1:0)-(n.map?1:0)}function HT(n){const e=new kT,t=BT(),i={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let c=0;c<9;c++)i.probe.push(new B);const r=new B,s=new Tt,o=new Tt;function a(c){let u=0,d=0,p=0;for(let b=0;b<9;b++)i.probe[b].set(0,0,0);let f=0,_=0,g=0,m=0,h=0,v=0,x=0,w=0,S=0,C=0,T=0;c.sort(VT);for(let b=0,y=c.length;b<y;b++){const P=c[b],D=P.color,O=P.intensity,V=P.distance,k=P.shadow&&P.shadow.map?P.shadow.map.texture:null;if(P.isAmbientLight)u+=D.r*O,d+=D.g*O,p+=D.b*O;else if(P.isLightProbe){for(let G=0;G<9;G++)i.probe[G].addScaledVector(P.sh.coefficients[G],O);T++}else if(P.isDirectionalLight){const G=e.get(P);if(G.color.copy(P.color).multiplyScalar(P.intensity),P.castShadow){const $=P.shadow,U=t.get(P);U.shadowIntensity=$.intensity,U.shadowBias=$.bias,U.shadowNormalBias=$.normalBias,U.shadowRadius=$.radius,U.shadowMapSize=$.mapSize,i.directionalShadow[f]=U,i.directionalShadowMap[f]=k,i.directionalShadowMatrix[f]=P.shadow.matrix,v++}i.directional[f]=G,f++}else if(P.isSpotLight){const G=e.get(P);G.position.setFromMatrixPosition(P.matrixWorld),G.color.copy(D).multiplyScalar(O),G.distance=V,G.coneCos=Math.cos(P.angle),G.penumbraCos=Math.cos(P.angle*(1-P.penumbra)),G.decay=P.decay,i.spot[g]=G;const $=P.shadow;if(P.map&&(i.spotLightMap[S]=P.map,S++,$.updateMatrices(P),P.castShadow&&C++),i.spotLightMatrix[g]=$.matrix,P.castShadow){const U=t.get(P);U.shadowIntensity=$.intensity,U.shadowBias=$.bias,U.shadowNormalBias=$.normalBias,U.shadowRadius=$.radius,U.shadowMapSize=$.mapSize,i.spotShadow[g]=U,i.spotShadowMap[g]=k,w++}g++}else if(P.isRectAreaLight){const G=e.get(P);G.color.copy(D).multiplyScalar(O),G.halfWidth.set(P.width*.5,0,0),G.halfHeight.set(0,P.height*.5,0),i.rectArea[m]=G,m++}else if(P.isPointLight){const G=e.get(P);if(G.color.copy(P.color).multiplyScalar(P.intensity),G.distance=P.distance,G.decay=P.decay,P.castShadow){const $=P.shadow,U=t.get(P);U.shadowIntensity=$.intensity,U.shadowBias=$.bias,U.shadowNormalBias=$.normalBias,U.shadowRadius=$.radius,U.shadowMapSize=$.mapSize,U.shadowCameraNear=$.camera.near,U.shadowCameraFar=$.camera.far,i.pointShadow[_]=U,i.pointShadowMap[_]=k,i.pointShadowMatrix[_]=P.shadow.matrix,x++}i.point[_]=G,_++}else if(P.isHemisphereLight){const G=e.get(P);G.skyColor.copy(P.color).multiplyScalar(O),G.groundColor.copy(P.groundColor).multiplyScalar(O),i.hemi[h]=G,h++}}m>0&&(n.has("OES_texture_float_linear")===!0?(i.rectAreaLTC1=ae.LTC_FLOAT_1,i.rectAreaLTC2=ae.LTC_FLOAT_2):(i.rectAreaLTC1=ae.LTC_HALF_1,i.rectAreaLTC2=ae.LTC_HALF_2)),i.ambient[0]=u,i.ambient[1]=d,i.ambient[2]=p;const A=i.hash;(A.directionalLength!==f||A.pointLength!==_||A.spotLength!==g||A.rectAreaLength!==m||A.hemiLength!==h||A.numDirectionalShadows!==v||A.numPointShadows!==x||A.numSpotShadows!==w||A.numSpotMaps!==S||A.numLightProbes!==T)&&(i.directional.length=f,i.spot.length=g,i.rectArea.length=m,i.point.length=_,i.hemi.length=h,i.directionalShadow.length=v,i.directionalShadowMap.length=v,i.pointShadow.length=x,i.pointShadowMap.length=x,i.spotShadow.length=w,i.spotShadowMap.length=w,i.directionalShadowMatrix.length=v,i.pointShadowMatrix.length=x,i.spotLightMatrix.length=w+S-C,i.spotLightMap.length=S,i.numSpotLightShadowsWithMaps=C,i.numLightProbes=T,A.directionalLength=f,A.pointLength=_,A.spotLength=g,A.rectAreaLength=m,A.hemiLength=h,A.numDirectionalShadows=v,A.numPointShadows=x,A.numSpotShadows=w,A.numSpotMaps=S,A.numLightProbes=T,i.version=zT++)}function l(c,u){let d=0,p=0,f=0,_=0,g=0;const m=u.matrixWorldInverse;for(let h=0,v=c.length;h<v;h++){const x=c[h];if(x.isDirectionalLight){const w=i.directional[d];w.direction.setFromMatrixPosition(x.matrixWorld),r.setFromMatrixPosition(x.target.matrixWorld),w.direction.sub(r),w.direction.transformDirection(m),d++}else if(x.isSpotLight){const w=i.spot[f];w.position.setFromMatrixPosition(x.matrixWorld),w.position.applyMatrix4(m),w.direction.setFromMatrixPosition(x.matrixWorld),r.setFromMatrixPosition(x.target.matrixWorld),w.direction.sub(r),w.direction.transformDirection(m),f++}else if(x.isRectAreaLight){const w=i.rectArea[_];w.position.setFromMatrixPosition(x.matrixWorld),w.position.applyMatrix4(m),o.identity(),s.copy(x.matrixWorld),s.premultiply(m),o.extractRotation(s),w.halfWidth.set(x.width*.5,0,0),w.halfHeight.set(0,x.height*.5,0),w.halfWidth.applyMatrix4(o),w.halfHeight.applyMatrix4(o),_++}else if(x.isPointLight){const w=i.point[p];w.position.setFromMatrixPosition(x.matrixWorld),w.position.applyMatrix4(m),p++}else if(x.isHemisphereLight){const w=i.hemi[g];w.direction.setFromMatrixPosition(x.matrixWorld),w.direction.transformDirection(m),g++}}}return{setup:a,setupView:l,state:i}}function qh(n){const e=new HT(n),t=[],i=[];function r(u){c.camera=u,t.length=0,i.length=0}function s(u){t.push(u)}function o(u){i.push(u)}function a(){e.setup(t)}function l(u){e.setupView(t,u)}const c={lightsArray:t,shadowsArray:i,camera:null,lights:e,transmissionRenderTarget:{}};return{init:r,state:c,setupLights:a,setupLightsView:l,pushLight:s,pushShadow:o}}function GT(n){let e=new WeakMap;function t(r,s=0){const o=e.get(r);let a;return o===void 0?(a=new qh(n),e.set(r,[a])):s>=o.length?(a=new qh(n),o.push(a)):a=o[s],a}function i(){e=new WeakMap}return{get:t,dispose:i}}const WT=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,XT=`uniform sampler2D shadow_pass;
uniform vec2 resolution;
uniform float radius;
#include <packing>
void main() {
	const float samples = float( VSM_SAMPLES );
	float mean = 0.0;
	float squared_mean = 0.0;
	float uvStride = samples <= 1.0 ? 0.0 : 2.0 / ( samples - 1.0 );
	float uvStart = samples <= 1.0 ? 0.0 : - 1.0;
	for ( float i = 0.0; i < samples; i ++ ) {
		float uvOffset = uvStart + i * uvStride;
		#ifdef HORIZONTAL_PASS
			vec2 distribution = unpackRGBATo2Half( texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( uvOffset, 0.0 ) * radius ) / resolution ) );
			mean += distribution.x;
			squared_mean += distribution.y * distribution.y + distribution.x * distribution.x;
		#else
			float depth = unpackRGBAToDepth( texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( 0.0, uvOffset ) * radius ) / resolution ) );
			mean += depth;
			squared_mean += depth * depth;
		#endif
	}
	mean = mean / samples;
	squared_mean = squared_mean / samples;
	float std_dev = sqrt( squared_mean - mean * mean );
	gl_FragColor = pack2HalfToRGBA( vec2( mean, std_dev ) );
}`;function $T(n,e,t){let i=new lm;const r=new Be,s=new Be,o=new yt,a=new fb({depthPacking:uy}),l=new pb,c={},u=t.maxTextureSize,d={[Hi]:qt,[qt]:Hi,[hi]:hi},p=new ti({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new Be},radius:{value:4}},vertexShader:WT,fragmentShader:XT}),f=p.clone();f.defines.HORIZONTAL_PASS=1;const _=new yi;_.setAttribute("position",new Zn(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const g=new jn(_,p),m=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=Bp;let h=this.type;this.render=function(C,T,A){if(m.enabled===!1||m.autoUpdate===!1&&m.needsUpdate===!1||C.length===0)return;const b=n.getRenderTarget(),y=n.getActiveCubeFace(),P=n.getActiveMipmapLevel(),D=n.state;D.setBlending(ki),D.buffers.depth.getReversed()===!0?D.buffers.color.setClear(0,0,0,0):D.buffers.color.setClear(1,1,1,1),D.buffers.depth.setTest(!0),D.setScissorTest(!1);const O=h!==ci&&this.type===ci,V=h===ci&&this.type!==ci;for(let k=0,G=C.length;k<G;k++){const $=C[k],U=$.shadow;if(U===void 0){console.warn("THREE.WebGLShadowMap:",$,"has no shadow.");continue}if(U.autoUpdate===!1&&U.needsUpdate===!1)continue;r.copy(U.mapSize);const Z=U.getFrameExtents();if(r.multiply(Z),s.copy(U.mapSize),(r.x>u||r.y>u)&&(r.x>u&&(s.x=Math.floor(u/Z.x),r.x=s.x*Z.x,U.mapSize.x=s.x),r.y>u&&(s.y=Math.floor(u/Z.y),r.y=s.y*Z.y,U.mapSize.y=s.y)),U.map===null||O===!0||V===!0){const ce=this.type!==ci?{minFilter:kn,magFilter:kn}:{};U.map!==null&&U.map.dispose(),U.map=new xr(r.x,r.y,ce),U.map.texture.name=$.name+".shadowMap",U.camera.updateProjectionMatrix()}n.setRenderTarget(U.map),n.clear();const ee=U.getViewportCount();for(let ce=0;ce<ee;ce++){const Ae=U.getViewport(ce);o.set(s.x*Ae.x,s.y*Ae.y,s.x*Ae.z,s.y*Ae.w),D.viewport(o),U.updateMatrices($,ce),i=U.getFrustum(),w(T,A,U.camera,$,this.type)}U.isPointLightShadow!==!0&&this.type===ci&&v(U,A),U.needsUpdate=!1}h=this.type,m.needsUpdate=!1,n.setRenderTarget(b,y,P)};function v(C,T){const A=e.update(g);p.defines.VSM_SAMPLES!==C.blurSamples&&(p.defines.VSM_SAMPLES=C.blurSamples,f.defines.VSM_SAMPLES=C.blurSamples,p.needsUpdate=!0,f.needsUpdate=!0),C.mapPass===null&&(C.mapPass=new xr(r.x,r.y)),p.uniforms.shadow_pass.value=C.map.texture,p.uniforms.resolution.value=C.mapSize,p.uniforms.radius.value=C.radius,n.setRenderTarget(C.mapPass),n.clear(),n.renderBufferDirect(T,null,A,p,g,null),f.uniforms.shadow_pass.value=C.mapPass.texture,f.uniforms.resolution.value=C.mapSize,f.uniforms.radius.value=C.radius,n.setRenderTarget(C.map),n.clear(),n.renderBufferDirect(T,null,A,f,g,null)}function x(C,T,A,b){let y=null;const P=A.isPointLight===!0?C.customDistanceMaterial:C.customDepthMaterial;if(P!==void 0)y=P;else if(y=A.isPointLight===!0?l:a,n.localClippingEnabled&&T.clipShadows===!0&&Array.isArray(T.clippingPlanes)&&T.clippingPlanes.length!==0||T.displacementMap&&T.displacementScale!==0||T.alphaMap&&T.alphaTest>0||T.map&&T.alphaTest>0||T.alphaToCoverage===!0){const D=y.uuid,O=T.uuid;let V=c[D];V===void 0&&(V={},c[D]=V);let k=V[O];k===void 0&&(k=y.clone(),V[O]=k,T.addEventListener("dispose",S)),y=k}if(y.visible=T.visible,y.wireframe=T.wireframe,b===ci?y.side=T.shadowSide!==null?T.shadowSide:T.side:y.side=T.shadowSide!==null?T.shadowSide:d[T.side],y.alphaMap=T.alphaMap,y.alphaTest=T.alphaToCoverage===!0?.5:T.alphaTest,y.map=T.map,y.clipShadows=T.clipShadows,y.clippingPlanes=T.clippingPlanes,y.clipIntersection=T.clipIntersection,y.displacementMap=T.displacementMap,y.displacementScale=T.displacementScale,y.displacementBias=T.displacementBias,y.wireframeLinewidth=T.wireframeLinewidth,y.linewidth=T.linewidth,A.isPointLight===!0&&y.isMeshDistanceMaterial===!0){const D=n.properties.get(y);D.light=A}return y}function w(C,T,A,b,y){if(C.visible===!1)return;if(C.layers.test(T.layers)&&(C.isMesh||C.isLine||C.isPoints)&&(C.castShadow||C.receiveShadow&&y===ci)&&(!C.frustumCulled||i.intersectsObject(C))){C.modelViewMatrix.multiplyMatrices(A.matrixWorldInverse,C.matrixWorld);const O=e.update(C),V=C.material;if(Array.isArray(V)){const k=O.groups;for(let G=0,$=k.length;G<$;G++){const U=k[G],Z=V[U.materialIndex];if(Z&&Z.visible){const ee=x(C,Z,b,y);C.onBeforeShadow(n,C,T,A,O,ee,U),n.renderBufferDirect(A,null,O,ee,C,U),C.onAfterShadow(n,C,T,A,O,ee,U)}}}else if(V.visible){const k=x(C,V,b,y);C.onBeforeShadow(n,C,T,A,O,k,null),n.renderBufferDirect(A,null,O,k,C,null),C.onAfterShadow(n,C,T,A,O,k,null)}}const D=C.children;for(let O=0,V=D.length;O<V;O++)w(D[O],T,A,b,y)}function S(C){C.target.removeEventListener("dispose",S);for(const A in c){const b=c[A],y=C.target.uuid;y in b&&(b[y].dispose(),delete b[y])}}}const qT={[dc]:hc,[fc]:gc,[pc]:_c,[ss]:mc,[hc]:dc,[gc]:fc,[_c]:pc,[mc]:ss};function YT(n,e){function t(){let I=!1;const re=new yt;let oe=null;const fe=new yt(0,0,0,0);return{setMask:function(te){oe!==te&&!I&&(n.colorMask(te,te,te,te),oe=te)},setLocked:function(te){I=te},setClear:function(te,K,ge,Ie,st){st===!0&&(te*=Ie,K*=Ie,ge*=Ie),re.set(te,K,ge,Ie),fe.equals(re)===!1&&(n.clearColor(te,K,ge,Ie),fe.copy(re))},reset:function(){I=!1,oe=null,fe.set(-1,0,0,0)}}}function i(){let I=!1,re=!1,oe=null,fe=null,te=null;return{setReversed:function(K){if(re!==K){const ge=e.get("EXT_clip_control");K?ge.clipControlEXT(ge.LOWER_LEFT_EXT,ge.ZERO_TO_ONE_EXT):ge.clipControlEXT(ge.LOWER_LEFT_EXT,ge.NEGATIVE_ONE_TO_ONE_EXT),re=K;const Ie=te;te=null,this.setClear(Ie)}},getReversed:function(){return re},setTest:function(K){K?Q(n.DEPTH_TEST):pe(n.DEPTH_TEST)},setMask:function(K){oe!==K&&!I&&(n.depthMask(K),oe=K)},setFunc:function(K){if(re&&(K=qT[K]),fe!==K){switch(K){case dc:n.depthFunc(n.NEVER);break;case hc:n.depthFunc(n.ALWAYS);break;case fc:n.depthFunc(n.LESS);break;case ss:n.depthFunc(n.LEQUAL);break;case pc:n.depthFunc(n.EQUAL);break;case mc:n.depthFunc(n.GEQUAL);break;case gc:n.depthFunc(n.GREATER);break;case _c:n.depthFunc(n.NOTEQUAL);break;default:n.depthFunc(n.LEQUAL)}fe=K}},setLocked:function(K){I=K},setClear:function(K){te!==K&&(re&&(K=1-K),n.clearDepth(K),te=K)},reset:function(){I=!1,oe=null,fe=null,te=null,re=!1}}}function r(){let I=!1,re=null,oe=null,fe=null,te=null,K=null,ge=null,Ie=null,st=null;return{setTest:function(Ke){I||(Ke?Q(n.STENCIL_TEST):pe(n.STENCIL_TEST))},setMask:function(Ke){re!==Ke&&!I&&(n.stencilMask(Ke),re=Ke)},setFunc:function(Ke,ii,zn){(oe!==Ke||fe!==ii||te!==zn)&&(n.stencilFunc(Ke,ii,zn),oe=Ke,fe=ii,te=zn)},setOp:function(Ke,ii,zn){(K!==Ke||ge!==ii||Ie!==zn)&&(n.stencilOp(Ke,ii,zn),K=Ke,ge=ii,Ie=zn)},setLocked:function(Ke){I=Ke},setClear:function(Ke){st!==Ke&&(n.clearStencil(Ke),st=Ke)},reset:function(){I=!1,re=null,oe=null,fe=null,te=null,K=null,ge=null,Ie=null,st=null}}}const s=new t,o=new i,a=new r,l=new WeakMap,c=new WeakMap;let u={},d={},p=new WeakMap,f=[],_=null,g=!1,m=null,h=null,v=null,x=null,w=null,S=null,C=null,T=new Ze(0,0,0),A=0,b=!1,y=null,P=null,D=null,O=null,V=null;const k=n.getParameter(n.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let G=!1,$=0;const U=n.getParameter(n.VERSION);U.indexOf("WebGL")!==-1?($=parseFloat(/^WebGL (\d)/.exec(U)[1]),G=$>=1):U.indexOf("OpenGL ES")!==-1&&($=parseFloat(/^OpenGL ES (\d)/.exec(U)[1]),G=$>=2);let Z=null,ee={};const ce=n.getParameter(n.SCISSOR_BOX),Ae=n.getParameter(n.VIEWPORT),Je=new yt().fromArray(ce),We=new yt().fromArray(Ae);function ze(I,re,oe,fe){const te=new Uint8Array(4),K=n.createTexture();n.bindTexture(I,K),n.texParameteri(I,n.TEXTURE_MIN_FILTER,n.NEAREST),n.texParameteri(I,n.TEXTURE_MAG_FILTER,n.NEAREST);for(let ge=0;ge<oe;ge++)I===n.TEXTURE_3D||I===n.TEXTURE_2D_ARRAY?n.texImage3D(re,0,n.RGBA,1,1,fe,0,n.RGBA,n.UNSIGNED_BYTE,te):n.texImage2D(re+ge,0,n.RGBA,1,1,0,n.RGBA,n.UNSIGNED_BYTE,te);return K}const j={};j[n.TEXTURE_2D]=ze(n.TEXTURE_2D,n.TEXTURE_2D,1),j[n.TEXTURE_CUBE_MAP]=ze(n.TEXTURE_CUBE_MAP,n.TEXTURE_CUBE_MAP_POSITIVE_X,6),j[n.TEXTURE_2D_ARRAY]=ze(n.TEXTURE_2D_ARRAY,n.TEXTURE_2D_ARRAY,1,1),j[n.TEXTURE_3D]=ze(n.TEXTURE_3D,n.TEXTURE_3D,1,1),s.setClear(0,0,0,1),o.setClear(1),a.setClear(0),Q(n.DEPTH_TEST),o.setFunc(ss),Re(!1),_e(Zd),Q(n.CULL_FACE),ct(ki);function Q(I){u[I]!==!0&&(n.enable(I),u[I]=!0)}function pe(I){u[I]!==!1&&(n.disable(I),u[I]=!1)}function Le(I,re){return d[I]!==re?(n.bindFramebuffer(I,re),d[I]=re,I===n.DRAW_FRAMEBUFFER&&(d[n.FRAMEBUFFER]=re),I===n.FRAMEBUFFER&&(d[n.DRAW_FRAMEBUFFER]=re),!0):!1}function Se(I,re){let oe=f,fe=!1;if(I){oe=p.get(re),oe===void 0&&(oe=[],p.set(re,oe));const te=I.textures;if(oe.length!==te.length||oe[0]!==n.COLOR_ATTACHMENT0){for(let K=0,ge=te.length;K<ge;K++)oe[K]=n.COLOR_ATTACHMENT0+K;oe.length=te.length,fe=!0}}else oe[0]!==n.BACK&&(oe[0]=n.BACK,fe=!0);fe&&n.drawBuffers(oe)}function Xe(I){return _!==I?(n.useProgram(I),_=I,!0):!1}const Nt={[sr]:n.FUNC_ADD,[Fw]:n.FUNC_SUBTRACT,[Nw]:n.FUNC_REVERSE_SUBTRACT};Nt[kw]=n.MIN,Nt[Bw]=n.MAX;const L={[zw]:n.ZERO,[Vw]:n.ONE,[Hw]:n.SRC_COLOR,[cc]:n.SRC_ALPHA,[Yw]:n.SRC_ALPHA_SATURATE,[$w]:n.DST_COLOR,[Ww]:n.DST_ALPHA,[Gw]:n.ONE_MINUS_SRC_COLOR,[uc]:n.ONE_MINUS_SRC_ALPHA,[qw]:n.ONE_MINUS_DST_COLOR,[Xw]:n.ONE_MINUS_DST_ALPHA,[jw]:n.CONSTANT_COLOR,[Kw]:n.ONE_MINUS_CONSTANT_COLOR,[Zw]:n.CONSTANT_ALPHA,[Jw]:n.ONE_MINUS_CONSTANT_ALPHA};function ct(I,re,oe,fe,te,K,ge,Ie,st,Ke){if(I===ki){g===!0&&(pe(n.BLEND),g=!1);return}if(g===!1&&(Q(n.BLEND),g=!0),I!==Ow){if(I!==m||Ke!==b){if((h!==sr||w!==sr)&&(n.blendEquation(n.FUNC_ADD),h=sr,w=sr),Ke)switch(I){case Zr:n.blendFuncSeparate(n.ONE,n.ONE_MINUS_SRC_ALPHA,n.ONE,n.ONE_MINUS_SRC_ALPHA);break;case lc:n.blendFunc(n.ONE,n.ONE);break;case Jd:n.blendFuncSeparate(n.ZERO,n.ONE_MINUS_SRC_COLOR,n.ZERO,n.ONE);break;case Qd:n.blendFuncSeparate(n.DST_COLOR,n.ONE_MINUS_SRC_ALPHA,n.ZERO,n.ONE);break;default:console.error("THREE.WebGLState: Invalid blending: ",I);break}else switch(I){case Zr:n.blendFuncSeparate(n.SRC_ALPHA,n.ONE_MINUS_SRC_ALPHA,n.ONE,n.ONE_MINUS_SRC_ALPHA);break;case lc:n.blendFuncSeparate(n.SRC_ALPHA,n.ONE,n.ONE,n.ONE);break;case Jd:console.error("THREE.WebGLState: SubtractiveBlending requires material.premultipliedAlpha = true");break;case Qd:console.error("THREE.WebGLState: MultiplyBlending requires material.premultipliedAlpha = true");break;default:console.error("THREE.WebGLState: Invalid blending: ",I);break}v=null,x=null,S=null,C=null,T.set(0,0,0),A=0,m=I,b=Ke}return}te=te||re,K=K||oe,ge=ge||fe,(re!==h||te!==w)&&(n.blendEquationSeparate(Nt[re],Nt[te]),h=re,w=te),(oe!==v||fe!==x||K!==S||ge!==C)&&(n.blendFuncSeparate(L[oe],L[fe],L[K],L[ge]),v=oe,x=fe,S=K,C=ge),(Ie.equals(T)===!1||st!==A)&&(n.blendColor(Ie.r,Ie.g,Ie.b,st),T.copy(Ie),A=st),m=I,b=!1}function Ue(I,re){I.side===hi?pe(n.CULL_FACE):Q(n.CULL_FACE);let oe=I.side===qt;re&&(oe=!oe),Re(oe),I.blending===Zr&&I.transparent===!1?ct(ki):ct(I.blending,I.blendEquation,I.blendSrc,I.blendDst,I.blendEquationAlpha,I.blendSrcAlpha,I.blendDstAlpha,I.blendColor,I.blendAlpha,I.premultipliedAlpha),o.setFunc(I.depthFunc),o.setTest(I.depthTest),o.setMask(I.depthWrite),s.setMask(I.colorWrite);const fe=I.stencilWrite;a.setTest(fe),fe&&(a.setMask(I.stencilWriteMask),a.setFunc(I.stencilFunc,I.stencilRef,I.stencilFuncMask),a.setOp(I.stencilFail,I.stencilZFail,I.stencilZPass)),ve(I.polygonOffset,I.polygonOffsetFactor,I.polygonOffsetUnits),I.alphaToCoverage===!0?Q(n.SAMPLE_ALPHA_TO_COVERAGE):pe(n.SAMPLE_ALPHA_TO_COVERAGE)}function Re(I){y!==I&&(I?n.frontFace(n.CW):n.frontFace(n.CCW),y=I)}function _e(I){I!==Lw?(Q(n.CULL_FACE),I!==P&&(I===Zd?n.cullFace(n.BACK):I===Iw?n.cullFace(n.FRONT):n.cullFace(n.FRONT_AND_BACK))):pe(n.CULL_FACE),P=I}function ut(I){I!==D&&(G&&n.lineWidth(I),D=I)}function ve(I,re,oe){I?(Q(n.POLYGON_OFFSET_FILL),(O!==re||V!==oe)&&(n.polygonOffset(re,oe),O=re,V=oe)):pe(n.POLYGON_OFFSET_FILL)}function Ne(I){I?Q(n.SCISSOR_TEST):pe(n.SCISSOR_TEST)}function Dt(I){I===void 0&&(I=n.TEXTURE0+k-1),Z!==I&&(n.activeTexture(I),Z=I)}function vt(I,re,oe){oe===void 0&&(Z===null?oe=n.TEXTURE0+k-1:oe=Z);let fe=ee[oe];fe===void 0&&(fe={type:void 0,texture:void 0},ee[oe]=fe),(fe.type!==I||fe.texture!==re)&&(Z!==oe&&(n.activeTexture(oe),Z=oe),n.bindTexture(I,re||j[I]),fe.type=I,fe.texture=re)}function R(){const I=ee[Z];I!==void 0&&I.type!==void 0&&(n.bindTexture(I.type,null),I.type=void 0,I.texture=void 0)}function E(){try{n.compressedTexImage2D(...arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function z(){try{n.compressedTexImage3D(...arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Y(){try{n.texSubImage2D(...arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function J(){try{n.texSubImage3D(...arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function q(){try{n.compressedTexSubImage2D(...arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function be(){try{n.compressedTexSubImage3D(...arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function se(){try{n.texStorage2D(...arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function xe(){try{n.texStorage3D(...arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function we(){try{n.texImage2D(...arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function ie(){try{n.texImage3D(...arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function de(I){Je.equals(I)===!1&&(n.scissor(I.x,I.y,I.z,I.w),Je.copy(I))}function Pe(I){We.equals(I)===!1&&(n.viewport(I.x,I.y,I.z,I.w),We.copy(I))}function ye(I,re){let oe=c.get(re);oe===void 0&&(oe=new WeakMap,c.set(re,oe));let fe=oe.get(I);fe===void 0&&(fe=n.getUniformBlockIndex(re,I.name),oe.set(I,fe))}function le(I,re){const fe=c.get(re).get(I);l.get(re)!==fe&&(n.uniformBlockBinding(re,fe,I.__bindingPointIndex),l.set(re,fe))}function Oe(){n.disable(n.BLEND),n.disable(n.CULL_FACE),n.disable(n.DEPTH_TEST),n.disable(n.POLYGON_OFFSET_FILL),n.disable(n.SCISSOR_TEST),n.disable(n.STENCIL_TEST),n.disable(n.SAMPLE_ALPHA_TO_COVERAGE),n.blendEquation(n.FUNC_ADD),n.blendFunc(n.ONE,n.ZERO),n.blendFuncSeparate(n.ONE,n.ZERO,n.ONE,n.ZERO),n.blendColor(0,0,0,0),n.colorMask(!0,!0,!0,!0),n.clearColor(0,0,0,0),n.depthMask(!0),n.depthFunc(n.LESS),o.setReversed(!1),n.clearDepth(1),n.stencilMask(4294967295),n.stencilFunc(n.ALWAYS,0,4294967295),n.stencilOp(n.KEEP,n.KEEP,n.KEEP),n.clearStencil(0),n.cullFace(n.BACK),n.frontFace(n.CCW),n.polygonOffset(0,0),n.activeTexture(n.TEXTURE0),n.bindFramebuffer(n.FRAMEBUFFER,null),n.bindFramebuffer(n.DRAW_FRAMEBUFFER,null),n.bindFramebuffer(n.READ_FRAMEBUFFER,null),n.useProgram(null),n.lineWidth(1),n.scissor(0,0,n.canvas.width,n.canvas.height),n.viewport(0,0,n.canvas.width,n.canvas.height),u={},Z=null,ee={},d={},p=new WeakMap,f=[],_=null,g=!1,m=null,h=null,v=null,x=null,w=null,S=null,C=null,T=new Ze(0,0,0),A=0,b=!1,y=null,P=null,D=null,O=null,V=null,Je.set(0,0,n.canvas.width,n.canvas.height),We.set(0,0,n.canvas.width,n.canvas.height),s.reset(),o.reset(),a.reset()}return{buffers:{color:s,depth:o,stencil:a},enable:Q,disable:pe,bindFramebuffer:Le,drawBuffers:Se,useProgram:Xe,setBlending:ct,setMaterial:Ue,setFlipSided:Re,setCullFace:_e,setLineWidth:ut,setPolygonOffset:ve,setScissorTest:Ne,activeTexture:Dt,bindTexture:vt,unbindTexture:R,compressedTexImage2D:E,compressedTexImage3D:z,texImage2D:we,texImage3D:ie,updateUBOMapping:ye,uniformBlockBinding:le,texStorage2D:se,texStorage3D:xe,texSubImage2D:Y,texSubImage3D:J,compressedTexSubImage2D:q,compressedTexSubImage3D:be,scissor:de,viewport:Pe,reset:Oe}}function jT(n,e,t,i,r,s,o){const a=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,l=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),c=new Be,u=new WeakMap;let d;const p=new WeakMap;let f=!1;try{f=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function _(R,E){return f?new OffscreenCanvas(R,E):Zs("canvas")}function g(R,E,z){let Y=1;const J=vt(R);if((J.width>z||J.height>z)&&(Y=z/Math.max(J.width,J.height)),Y<1)if(typeof HTMLImageElement<"u"&&R instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&R instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&R instanceof ImageBitmap||typeof VideoFrame<"u"&&R instanceof VideoFrame){const q=Math.floor(Y*J.width),be=Math.floor(Y*J.height);d===void 0&&(d=_(q,be));const se=E?_(q,be):d;return se.width=q,se.height=be,se.getContext("2d").drawImage(R,0,0,q,be),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+J.width+"x"+J.height+") to ("+q+"x"+be+")."),se}else return"data"in R&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+J.width+"x"+J.height+")."),R;return R}function m(R){return R.generateMipmaps}function h(R){n.generateMipmap(R)}function v(R){return R.isWebGLCubeRenderTarget?n.TEXTURE_CUBE_MAP:R.isWebGL3DRenderTarget?n.TEXTURE_3D:R.isWebGLArrayRenderTarget||R.isCompressedArrayTexture?n.TEXTURE_2D_ARRAY:n.TEXTURE_2D}function x(R,E,z,Y,J=!1){if(R!==null){if(n[R]!==void 0)return n[R];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+R+"'")}let q=E;if(E===n.RED&&(z===n.FLOAT&&(q=n.R32F),z===n.HALF_FLOAT&&(q=n.R16F),z===n.UNSIGNED_BYTE&&(q=n.R8)),E===n.RED_INTEGER&&(z===n.UNSIGNED_BYTE&&(q=n.R8UI),z===n.UNSIGNED_SHORT&&(q=n.R16UI),z===n.UNSIGNED_INT&&(q=n.R32UI),z===n.BYTE&&(q=n.R8I),z===n.SHORT&&(q=n.R16I),z===n.INT&&(q=n.R32I)),E===n.RG&&(z===n.FLOAT&&(q=n.RG32F),z===n.HALF_FLOAT&&(q=n.RG16F),z===n.UNSIGNED_BYTE&&(q=n.RG8)),E===n.RG_INTEGER&&(z===n.UNSIGNED_BYTE&&(q=n.RG8UI),z===n.UNSIGNED_SHORT&&(q=n.RG16UI),z===n.UNSIGNED_INT&&(q=n.RG32UI),z===n.BYTE&&(q=n.RG8I),z===n.SHORT&&(q=n.RG16I),z===n.INT&&(q=n.RG32I)),E===n.RGB_INTEGER&&(z===n.UNSIGNED_BYTE&&(q=n.RGB8UI),z===n.UNSIGNED_SHORT&&(q=n.RGB16UI),z===n.UNSIGNED_INT&&(q=n.RGB32UI),z===n.BYTE&&(q=n.RGB8I),z===n.SHORT&&(q=n.RGB16I),z===n.INT&&(q=n.RGB32I)),E===n.RGBA_INTEGER&&(z===n.UNSIGNED_BYTE&&(q=n.RGBA8UI),z===n.UNSIGNED_SHORT&&(q=n.RGBA16UI),z===n.UNSIGNED_INT&&(q=n.RGBA32UI),z===n.BYTE&&(q=n.RGBA8I),z===n.SHORT&&(q=n.RGBA16I),z===n.INT&&(q=n.RGBA32I)),E===n.RGB&&(z===n.UNSIGNED_INT_5_9_9_9_REV&&(q=n.RGB9_E5),z===n.UNSIGNED_INT_10F_11F_11F_REV&&(q=n.R11F_G11F_B10F)),E===n.RGBA){const be=J?ba:qe.getTransfer(Y);z===n.FLOAT&&(q=n.RGBA32F),z===n.HALF_FLOAT&&(q=n.RGBA16F),z===n.UNSIGNED_BYTE&&(q=be===et?n.SRGB8_ALPHA8:n.RGBA8),z===n.UNSIGNED_SHORT_4_4_4_4&&(q=n.RGBA4),z===n.UNSIGNED_SHORT_5_5_5_1&&(q=n.RGB5_A1)}return(q===n.R16F||q===n.R32F||q===n.RG16F||q===n.RG32F||q===n.RGBA16F||q===n.RGBA32F)&&e.get("EXT_color_buffer_float"),q}function w(R,E){let z;return R?E===null||E===_r||E===qs?z=n.DEPTH24_STENCIL8:E===fi?z=n.DEPTH32F_STENCIL8:E===$s&&(z=n.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):E===null||E===_r||E===qs?z=n.DEPTH_COMPONENT24:E===fi?z=n.DEPTH_COMPONENT32F:E===$s&&(z=n.DEPTH_COMPONENT16),z}function S(R,E){return m(R)===!0||R.isFramebufferTexture&&R.minFilter!==kn&&R.minFilter!==qn?Math.log2(Math.max(E.width,E.height))+1:R.mipmaps!==void 0&&R.mipmaps.length>0?R.mipmaps.length:R.isCompressedTexture&&Array.isArray(R.image)?E.mipmaps.length:1}function C(R){const E=R.target;E.removeEventListener("dispose",C),A(E),E.isVideoTexture&&u.delete(E)}function T(R){const E=R.target;E.removeEventListener("dispose",T),y(E)}function A(R){const E=i.get(R);if(E.__webglInit===void 0)return;const z=R.source,Y=p.get(z);if(Y){const J=Y[E.__cacheKey];J.usedTimes--,J.usedTimes===0&&b(R),Object.keys(Y).length===0&&p.delete(z)}i.remove(R)}function b(R){const E=i.get(R);n.deleteTexture(E.__webglTexture);const z=R.source,Y=p.get(z);delete Y[E.__cacheKey],o.memory.textures--}function y(R){const E=i.get(R);if(R.depthTexture&&(R.depthTexture.dispose(),i.remove(R.depthTexture)),R.isWebGLCubeRenderTarget)for(let Y=0;Y<6;Y++){if(Array.isArray(E.__webglFramebuffer[Y]))for(let J=0;J<E.__webglFramebuffer[Y].length;J++)n.deleteFramebuffer(E.__webglFramebuffer[Y][J]);else n.deleteFramebuffer(E.__webglFramebuffer[Y]);E.__webglDepthbuffer&&n.deleteRenderbuffer(E.__webglDepthbuffer[Y])}else{if(Array.isArray(E.__webglFramebuffer))for(let Y=0;Y<E.__webglFramebuffer.length;Y++)n.deleteFramebuffer(E.__webglFramebuffer[Y]);else n.deleteFramebuffer(E.__webglFramebuffer);if(E.__webglDepthbuffer&&n.deleteRenderbuffer(E.__webglDepthbuffer),E.__webglMultisampledFramebuffer&&n.deleteFramebuffer(E.__webglMultisampledFramebuffer),E.__webglColorRenderbuffer)for(let Y=0;Y<E.__webglColorRenderbuffer.length;Y++)E.__webglColorRenderbuffer[Y]&&n.deleteRenderbuffer(E.__webglColorRenderbuffer[Y]);E.__webglDepthRenderbuffer&&n.deleteRenderbuffer(E.__webglDepthRenderbuffer)}const z=R.textures;for(let Y=0,J=z.length;Y<J;Y++){const q=i.get(z[Y]);q.__webglTexture&&(n.deleteTexture(q.__webglTexture),o.memory.textures--),i.remove(z[Y])}i.remove(R)}let P=0;function D(){P=0}function O(){const R=P;return R>=r.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+R+" texture units while this GPU supports only "+r.maxTextures),P+=1,R}function V(R){const E=[];return E.push(R.wrapS),E.push(R.wrapT),E.push(R.wrapR||0),E.push(R.magFilter),E.push(R.minFilter),E.push(R.anisotropy),E.push(R.internalFormat),E.push(R.format),E.push(R.type),E.push(R.generateMipmaps),E.push(R.premultiplyAlpha),E.push(R.flipY),E.push(R.unpackAlignment),E.push(R.colorSpace),E.join()}function k(R,E){const z=i.get(R);if(R.isVideoTexture&&Ne(R),R.isRenderTargetTexture===!1&&R.isExternalTexture!==!0&&R.version>0&&z.__version!==R.version){const Y=R.image;if(Y===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(Y.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{j(z,R,E);return}}else R.isExternalTexture&&(z.__webglTexture=R.sourceTexture?R.sourceTexture:null);t.bindTexture(n.TEXTURE_2D,z.__webglTexture,n.TEXTURE0+E)}function G(R,E){const z=i.get(R);if(R.isRenderTargetTexture===!1&&R.version>0&&z.__version!==R.version){j(z,R,E);return}t.bindTexture(n.TEXTURE_2D_ARRAY,z.__webglTexture,n.TEXTURE0+E)}function $(R,E){const z=i.get(R);if(R.isRenderTargetTexture===!1&&R.version>0&&z.__version!==R.version){j(z,R,E);return}t.bindTexture(n.TEXTURE_3D,z.__webglTexture,n.TEXTURE0+E)}function U(R,E){const z=i.get(R);if(R.version>0&&z.__version!==R.version){Q(z,R,E);return}t.bindTexture(n.TEXTURE_CUBE_MAP,z.__webglTexture,n.TEXTURE0+E)}const Z={[wc]:n.REPEAT,[lr]:n.CLAMP_TO_EDGE,[yc]:n.MIRRORED_REPEAT},ee={[kn]:n.NEAREST,[ly]:n.NEAREST_MIPMAP_NEAREST,[Mo]:n.NEAREST_MIPMAP_LINEAR,[qn]:n.LINEAR,[dl]:n.LINEAR_MIPMAP_NEAREST,[cr]:n.LINEAR_MIPMAP_LINEAR},ce={[fy]:n.NEVER,[xy]:n.ALWAYS,[py]:n.LESS,[Kp]:n.LEQUAL,[my]:n.EQUAL,[vy]:n.GEQUAL,[gy]:n.GREATER,[_y]:n.NOTEQUAL};function Ae(R,E){if(E.type===fi&&e.has("OES_texture_float_linear")===!1&&(E.magFilter===qn||E.magFilter===dl||E.magFilter===Mo||E.magFilter===cr||E.minFilter===qn||E.minFilter===dl||E.minFilter===Mo||E.minFilter===cr)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),n.texParameteri(R,n.TEXTURE_WRAP_S,Z[E.wrapS]),n.texParameteri(R,n.TEXTURE_WRAP_T,Z[E.wrapT]),(R===n.TEXTURE_3D||R===n.TEXTURE_2D_ARRAY)&&n.texParameteri(R,n.TEXTURE_WRAP_R,Z[E.wrapR]),n.texParameteri(R,n.TEXTURE_MAG_FILTER,ee[E.magFilter]),n.texParameteri(R,n.TEXTURE_MIN_FILTER,ee[E.minFilter]),E.compareFunction&&(n.texParameteri(R,n.TEXTURE_COMPARE_MODE,n.COMPARE_REF_TO_TEXTURE),n.texParameteri(R,n.TEXTURE_COMPARE_FUNC,ce[E.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(E.magFilter===kn||E.minFilter!==Mo&&E.minFilter!==cr||E.type===fi&&e.has("OES_texture_float_linear")===!1)return;if(E.anisotropy>1||i.get(E).__currentAnisotropy){const z=e.get("EXT_texture_filter_anisotropic");n.texParameterf(R,z.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(E.anisotropy,r.getMaxAnisotropy())),i.get(E).__currentAnisotropy=E.anisotropy}}}function Je(R,E){let z=!1;R.__webglInit===void 0&&(R.__webglInit=!0,E.addEventListener("dispose",C));const Y=E.source;let J=p.get(Y);J===void 0&&(J={},p.set(Y,J));const q=V(E);if(q!==R.__cacheKey){J[q]===void 0&&(J[q]={texture:n.createTexture(),usedTimes:0},o.memory.textures++,z=!0),J[q].usedTimes++;const be=J[R.__cacheKey];be!==void 0&&(J[R.__cacheKey].usedTimes--,be.usedTimes===0&&b(E)),R.__cacheKey=q,R.__webglTexture=J[q].texture}return z}function We(R,E,z){return Math.floor(Math.floor(R/z)/E)}function ze(R,E,z,Y){const q=R.updateRanges;if(q.length===0)t.texSubImage2D(n.TEXTURE_2D,0,0,0,E.width,E.height,z,Y,E.data);else{q.sort((ie,de)=>ie.start-de.start);let be=0;for(let ie=1;ie<q.length;ie++){const de=q[be],Pe=q[ie],ye=de.start+de.count,le=We(Pe.start,E.width,4),Oe=We(de.start,E.width,4);Pe.start<=ye+1&&le===Oe&&We(Pe.start+Pe.count-1,E.width,4)===le?de.count=Math.max(de.count,Pe.start+Pe.count-de.start):(++be,q[be]=Pe)}q.length=be+1;const se=n.getParameter(n.UNPACK_ROW_LENGTH),xe=n.getParameter(n.UNPACK_SKIP_PIXELS),we=n.getParameter(n.UNPACK_SKIP_ROWS);n.pixelStorei(n.UNPACK_ROW_LENGTH,E.width);for(let ie=0,de=q.length;ie<de;ie++){const Pe=q[ie],ye=Math.floor(Pe.start/4),le=Math.ceil(Pe.count/4),Oe=ye%E.width,I=Math.floor(ye/E.width),re=le,oe=1;n.pixelStorei(n.UNPACK_SKIP_PIXELS,Oe),n.pixelStorei(n.UNPACK_SKIP_ROWS,I),t.texSubImage2D(n.TEXTURE_2D,0,Oe,I,re,oe,z,Y,E.data)}R.clearUpdateRanges(),n.pixelStorei(n.UNPACK_ROW_LENGTH,se),n.pixelStorei(n.UNPACK_SKIP_PIXELS,xe),n.pixelStorei(n.UNPACK_SKIP_ROWS,we)}}function j(R,E,z){let Y=n.TEXTURE_2D;(E.isDataArrayTexture||E.isCompressedArrayTexture)&&(Y=n.TEXTURE_2D_ARRAY),E.isData3DTexture&&(Y=n.TEXTURE_3D);const J=Je(R,E),q=E.source;t.bindTexture(Y,R.__webglTexture,n.TEXTURE0+z);const be=i.get(q);if(q.version!==be.__version||J===!0){t.activeTexture(n.TEXTURE0+z);const se=qe.getPrimaries(qe.workingColorSpace),xe=E.colorSpace===Pi?null:qe.getPrimaries(E.colorSpace),we=E.colorSpace===Pi||se===xe?n.NONE:n.BROWSER_DEFAULT_WEBGL;n.pixelStorei(n.UNPACK_FLIP_Y_WEBGL,E.flipY),n.pixelStorei(n.UNPACK_PREMULTIPLY_ALPHA_WEBGL,E.premultiplyAlpha),n.pixelStorei(n.UNPACK_ALIGNMENT,E.unpackAlignment),n.pixelStorei(n.UNPACK_COLORSPACE_CONVERSION_WEBGL,we);let ie=g(E.image,!1,r.maxTextureSize);ie=Dt(E,ie);const de=s.convert(E.format,E.colorSpace),Pe=s.convert(E.type);let ye=x(E.internalFormat,de,Pe,E.colorSpace,E.isVideoTexture);Ae(Y,E);let le;const Oe=E.mipmaps,I=E.isVideoTexture!==!0,re=be.__version===void 0||J===!0,oe=q.dataReady,fe=S(E,ie);if(E.isDepthTexture)ye=w(E.format===js,E.type),re&&(I?t.texStorage2D(n.TEXTURE_2D,1,ye,ie.width,ie.height):t.texImage2D(n.TEXTURE_2D,0,ye,ie.width,ie.height,0,de,Pe,null));else if(E.isDataTexture)if(Oe.length>0){I&&re&&t.texStorage2D(n.TEXTURE_2D,fe,ye,Oe[0].width,Oe[0].height);for(let te=0,K=Oe.length;te<K;te++)le=Oe[te],I?oe&&t.texSubImage2D(n.TEXTURE_2D,te,0,0,le.width,le.height,de,Pe,le.data):t.texImage2D(n.TEXTURE_2D,te,ye,le.width,le.height,0,de,Pe,le.data);E.generateMipmaps=!1}else I?(re&&t.texStorage2D(n.TEXTURE_2D,fe,ye,ie.width,ie.height),oe&&ze(E,ie,de,Pe)):t.texImage2D(n.TEXTURE_2D,0,ye,ie.width,ie.height,0,de,Pe,ie.data);else if(E.isCompressedTexture)if(E.isCompressedArrayTexture){I&&re&&t.texStorage3D(n.TEXTURE_2D_ARRAY,fe,ye,Oe[0].width,Oe[0].height,ie.depth);for(let te=0,K=Oe.length;te<K;te++)if(le=Oe[te],E.format!==Nn)if(de!==null)if(I){if(oe)if(E.layerUpdates.size>0){const ge=Sh(le.width,le.height,E.format,E.type);for(const Ie of E.layerUpdates){const st=le.data.subarray(Ie*ge/le.data.BYTES_PER_ELEMENT,(Ie+1)*ge/le.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(n.TEXTURE_2D_ARRAY,te,0,0,Ie,le.width,le.height,1,de,st)}E.clearLayerUpdates()}else t.compressedTexSubImage3D(n.TEXTURE_2D_ARRAY,te,0,0,0,le.width,le.height,ie.depth,de,le.data)}else t.compressedTexImage3D(n.TEXTURE_2D_ARRAY,te,ye,le.width,le.height,ie.depth,0,le.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else I?oe&&t.texSubImage3D(n.TEXTURE_2D_ARRAY,te,0,0,0,le.width,le.height,ie.depth,de,Pe,le.data):t.texImage3D(n.TEXTURE_2D_ARRAY,te,ye,le.width,le.height,ie.depth,0,de,Pe,le.data)}else{I&&re&&t.texStorage2D(n.TEXTURE_2D,fe,ye,Oe[0].width,Oe[0].height);for(let te=0,K=Oe.length;te<K;te++)le=Oe[te],E.format!==Nn?de!==null?I?oe&&t.compressedTexSubImage2D(n.TEXTURE_2D,te,0,0,le.width,le.height,de,le.data):t.compressedTexImage2D(n.TEXTURE_2D,te,ye,le.width,le.height,0,le.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):I?oe&&t.texSubImage2D(n.TEXTURE_2D,te,0,0,le.width,le.height,de,Pe,le.data):t.texImage2D(n.TEXTURE_2D,te,ye,le.width,le.height,0,de,Pe,le.data)}else if(E.isDataArrayTexture)if(I){if(re&&t.texStorage3D(n.TEXTURE_2D_ARRAY,fe,ye,ie.width,ie.height,ie.depth),oe)if(E.layerUpdates.size>0){const te=Sh(ie.width,ie.height,E.format,E.type);for(const K of E.layerUpdates){const ge=ie.data.subarray(K*te/ie.data.BYTES_PER_ELEMENT,(K+1)*te/ie.data.BYTES_PER_ELEMENT);t.texSubImage3D(n.TEXTURE_2D_ARRAY,0,0,0,K,ie.width,ie.height,1,de,Pe,ge)}E.clearLayerUpdates()}else t.texSubImage3D(n.TEXTURE_2D_ARRAY,0,0,0,0,ie.width,ie.height,ie.depth,de,Pe,ie.data)}else t.texImage3D(n.TEXTURE_2D_ARRAY,0,ye,ie.width,ie.height,ie.depth,0,de,Pe,ie.data);else if(E.isData3DTexture)I?(re&&t.texStorage3D(n.TEXTURE_3D,fe,ye,ie.width,ie.height,ie.depth),oe&&t.texSubImage3D(n.TEXTURE_3D,0,0,0,0,ie.width,ie.height,ie.depth,de,Pe,ie.data)):t.texImage3D(n.TEXTURE_3D,0,ye,ie.width,ie.height,ie.depth,0,de,Pe,ie.data);else if(E.isFramebufferTexture){if(re)if(I)t.texStorage2D(n.TEXTURE_2D,fe,ye,ie.width,ie.height);else{let te=ie.width,K=ie.height;for(let ge=0;ge<fe;ge++)t.texImage2D(n.TEXTURE_2D,ge,ye,te,K,0,de,Pe,null),te>>=1,K>>=1}}else if(Oe.length>0){if(I&&re){const te=vt(Oe[0]);t.texStorage2D(n.TEXTURE_2D,fe,ye,te.width,te.height)}for(let te=0,K=Oe.length;te<K;te++)le=Oe[te],I?oe&&t.texSubImage2D(n.TEXTURE_2D,te,0,0,de,Pe,le):t.texImage2D(n.TEXTURE_2D,te,ye,de,Pe,le);E.generateMipmaps=!1}else if(I){if(re){const te=vt(ie);t.texStorage2D(n.TEXTURE_2D,fe,ye,te.width,te.height)}oe&&t.texSubImage2D(n.TEXTURE_2D,0,0,0,de,Pe,ie)}else t.texImage2D(n.TEXTURE_2D,0,ye,de,Pe,ie);m(E)&&h(Y),be.__version=q.version,E.onUpdate&&E.onUpdate(E)}R.__version=E.version}function Q(R,E,z){if(E.image.length!==6)return;const Y=Je(R,E),J=E.source;t.bindTexture(n.TEXTURE_CUBE_MAP,R.__webglTexture,n.TEXTURE0+z);const q=i.get(J);if(J.version!==q.__version||Y===!0){t.activeTexture(n.TEXTURE0+z);const be=qe.getPrimaries(qe.workingColorSpace),se=E.colorSpace===Pi?null:qe.getPrimaries(E.colorSpace),xe=E.colorSpace===Pi||be===se?n.NONE:n.BROWSER_DEFAULT_WEBGL;n.pixelStorei(n.UNPACK_FLIP_Y_WEBGL,E.flipY),n.pixelStorei(n.UNPACK_PREMULTIPLY_ALPHA_WEBGL,E.premultiplyAlpha),n.pixelStorei(n.UNPACK_ALIGNMENT,E.unpackAlignment),n.pixelStorei(n.UNPACK_COLORSPACE_CONVERSION_WEBGL,xe);const we=E.isCompressedTexture||E.image[0].isCompressedTexture,ie=E.image[0]&&E.image[0].isDataTexture,de=[];for(let K=0;K<6;K++)!we&&!ie?de[K]=g(E.image[K],!0,r.maxCubemapSize):de[K]=ie?E.image[K].image:E.image[K],de[K]=Dt(E,de[K]);const Pe=de[0],ye=s.convert(E.format,E.colorSpace),le=s.convert(E.type),Oe=x(E.internalFormat,ye,le,E.colorSpace),I=E.isVideoTexture!==!0,re=q.__version===void 0||Y===!0,oe=J.dataReady;let fe=S(E,Pe);Ae(n.TEXTURE_CUBE_MAP,E);let te;if(we){I&&re&&t.texStorage2D(n.TEXTURE_CUBE_MAP,fe,Oe,Pe.width,Pe.height);for(let K=0;K<6;K++){te=de[K].mipmaps;for(let ge=0;ge<te.length;ge++){const Ie=te[ge];E.format!==Nn?ye!==null?I?oe&&t.compressedTexSubImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+K,ge,0,0,Ie.width,Ie.height,ye,Ie.data):t.compressedTexImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+K,ge,Oe,Ie.width,Ie.height,0,Ie.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):I?oe&&t.texSubImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+K,ge,0,0,Ie.width,Ie.height,ye,le,Ie.data):t.texImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+K,ge,Oe,Ie.width,Ie.height,0,ye,le,Ie.data)}}}else{if(te=E.mipmaps,I&&re){te.length>0&&fe++;const K=vt(de[0]);t.texStorage2D(n.TEXTURE_CUBE_MAP,fe,Oe,K.width,K.height)}for(let K=0;K<6;K++)if(ie){I?oe&&t.texSubImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+K,0,0,0,de[K].width,de[K].height,ye,le,de[K].data):t.texImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+K,0,Oe,de[K].width,de[K].height,0,ye,le,de[K].data);for(let ge=0;ge<te.length;ge++){const st=te[ge].image[K].image;I?oe&&t.texSubImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+K,ge+1,0,0,st.width,st.height,ye,le,st.data):t.texImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+K,ge+1,Oe,st.width,st.height,0,ye,le,st.data)}}else{I?oe&&t.texSubImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+K,0,0,0,ye,le,de[K]):t.texImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+K,0,Oe,ye,le,de[K]);for(let ge=0;ge<te.length;ge++){const Ie=te[ge];I?oe&&t.texSubImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+K,ge+1,0,0,ye,le,Ie.image[K]):t.texImage2D(n.TEXTURE_CUBE_MAP_POSITIVE_X+K,ge+1,Oe,ye,le,Ie.image[K])}}}m(E)&&h(n.TEXTURE_CUBE_MAP),q.__version=J.version,E.onUpdate&&E.onUpdate(E)}R.__version=E.version}function pe(R,E,z,Y,J,q){const be=s.convert(z.format,z.colorSpace),se=s.convert(z.type),xe=x(z.internalFormat,be,se,z.colorSpace),we=i.get(E),ie=i.get(z);if(ie.__renderTarget=E,!we.__hasExternalTextures){const de=Math.max(1,E.width>>q),Pe=Math.max(1,E.height>>q);J===n.TEXTURE_3D||J===n.TEXTURE_2D_ARRAY?t.texImage3D(J,q,xe,de,Pe,E.depth,0,be,se,null):t.texImage2D(J,q,xe,de,Pe,0,be,se,null)}t.bindFramebuffer(n.FRAMEBUFFER,R),ve(E)?a.framebufferTexture2DMultisampleEXT(n.FRAMEBUFFER,Y,J,ie.__webglTexture,0,ut(E)):(J===n.TEXTURE_2D||J>=n.TEXTURE_CUBE_MAP_POSITIVE_X&&J<=n.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&n.framebufferTexture2D(n.FRAMEBUFFER,Y,J,ie.__webglTexture,q),t.bindFramebuffer(n.FRAMEBUFFER,null)}function Le(R,E,z){if(n.bindRenderbuffer(n.RENDERBUFFER,R),E.depthBuffer){const Y=E.depthTexture,J=Y&&Y.isDepthTexture?Y.type:null,q=w(E.stencilBuffer,J),be=E.stencilBuffer?n.DEPTH_STENCIL_ATTACHMENT:n.DEPTH_ATTACHMENT,se=ut(E);ve(E)?a.renderbufferStorageMultisampleEXT(n.RENDERBUFFER,se,q,E.width,E.height):z?n.renderbufferStorageMultisample(n.RENDERBUFFER,se,q,E.width,E.height):n.renderbufferStorage(n.RENDERBUFFER,q,E.width,E.height),n.framebufferRenderbuffer(n.FRAMEBUFFER,be,n.RENDERBUFFER,R)}else{const Y=E.textures;for(let J=0;J<Y.length;J++){const q=Y[J],be=s.convert(q.format,q.colorSpace),se=s.convert(q.type),xe=x(q.internalFormat,be,se,q.colorSpace),we=ut(E);z&&ve(E)===!1?n.renderbufferStorageMultisample(n.RENDERBUFFER,we,xe,E.width,E.height):ve(E)?a.renderbufferStorageMultisampleEXT(n.RENDERBUFFER,we,xe,E.width,E.height):n.renderbufferStorage(n.RENDERBUFFER,xe,E.width,E.height)}}n.bindRenderbuffer(n.RENDERBUFFER,null)}function Se(R,E){if(E&&E.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(n.FRAMEBUFFER,R),!(E.depthTexture&&E.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");const Y=i.get(E.depthTexture);Y.__renderTarget=E,(!Y.__webglTexture||E.depthTexture.image.width!==E.width||E.depthTexture.image.height!==E.height)&&(E.depthTexture.image.width=E.width,E.depthTexture.image.height=E.height,E.depthTexture.needsUpdate=!0),k(E.depthTexture,0);const J=Y.__webglTexture,q=ut(E);if(E.depthTexture.format===Ys)ve(E)?a.framebufferTexture2DMultisampleEXT(n.FRAMEBUFFER,n.DEPTH_ATTACHMENT,n.TEXTURE_2D,J,0,q):n.framebufferTexture2D(n.FRAMEBUFFER,n.DEPTH_ATTACHMENT,n.TEXTURE_2D,J,0);else if(E.depthTexture.format===js)ve(E)?a.framebufferTexture2DMultisampleEXT(n.FRAMEBUFFER,n.DEPTH_STENCIL_ATTACHMENT,n.TEXTURE_2D,J,0,q):n.framebufferTexture2D(n.FRAMEBUFFER,n.DEPTH_STENCIL_ATTACHMENT,n.TEXTURE_2D,J,0);else throw new Error("Unknown depthTexture format")}function Xe(R){const E=i.get(R),z=R.isWebGLCubeRenderTarget===!0;if(E.__boundDepthTexture!==R.depthTexture){const Y=R.depthTexture;if(E.__depthDisposeCallback&&E.__depthDisposeCallback(),Y){const J=()=>{delete E.__boundDepthTexture,delete E.__depthDisposeCallback,Y.removeEventListener("dispose",J)};Y.addEventListener("dispose",J),E.__depthDisposeCallback=J}E.__boundDepthTexture=Y}if(R.depthTexture&&!E.__autoAllocateDepthBuffer){if(z)throw new Error("target.depthTexture not supported in Cube render targets");const Y=R.texture.mipmaps;Y&&Y.length>0?Se(E.__webglFramebuffer[0],R):Se(E.__webglFramebuffer,R)}else if(z){E.__webglDepthbuffer=[];for(let Y=0;Y<6;Y++)if(t.bindFramebuffer(n.FRAMEBUFFER,E.__webglFramebuffer[Y]),E.__webglDepthbuffer[Y]===void 0)E.__webglDepthbuffer[Y]=n.createRenderbuffer(),Le(E.__webglDepthbuffer[Y],R,!1);else{const J=R.stencilBuffer?n.DEPTH_STENCIL_ATTACHMENT:n.DEPTH_ATTACHMENT,q=E.__webglDepthbuffer[Y];n.bindRenderbuffer(n.RENDERBUFFER,q),n.framebufferRenderbuffer(n.FRAMEBUFFER,J,n.RENDERBUFFER,q)}}else{const Y=R.texture.mipmaps;if(Y&&Y.length>0?t.bindFramebuffer(n.FRAMEBUFFER,E.__webglFramebuffer[0]):t.bindFramebuffer(n.FRAMEBUFFER,E.__webglFramebuffer),E.__webglDepthbuffer===void 0)E.__webglDepthbuffer=n.createRenderbuffer(),Le(E.__webglDepthbuffer,R,!1);else{const J=R.stencilBuffer?n.DEPTH_STENCIL_ATTACHMENT:n.DEPTH_ATTACHMENT,q=E.__webglDepthbuffer;n.bindRenderbuffer(n.RENDERBUFFER,q),n.framebufferRenderbuffer(n.FRAMEBUFFER,J,n.RENDERBUFFER,q)}}t.bindFramebuffer(n.FRAMEBUFFER,null)}function Nt(R,E,z){const Y=i.get(R);E!==void 0&&pe(Y.__webglFramebuffer,R,R.texture,n.COLOR_ATTACHMENT0,n.TEXTURE_2D,0),z!==void 0&&Xe(R)}function L(R){const E=R.texture,z=i.get(R),Y=i.get(E);R.addEventListener("dispose",T);const J=R.textures,q=R.isWebGLCubeRenderTarget===!0,be=J.length>1;if(be||(Y.__webglTexture===void 0&&(Y.__webglTexture=n.createTexture()),Y.__version=E.version,o.memory.textures++),q){z.__webglFramebuffer=[];for(let se=0;se<6;se++)if(E.mipmaps&&E.mipmaps.length>0){z.__webglFramebuffer[se]=[];for(let xe=0;xe<E.mipmaps.length;xe++)z.__webglFramebuffer[se][xe]=n.createFramebuffer()}else z.__webglFramebuffer[se]=n.createFramebuffer()}else{if(E.mipmaps&&E.mipmaps.length>0){z.__webglFramebuffer=[];for(let se=0;se<E.mipmaps.length;se++)z.__webglFramebuffer[se]=n.createFramebuffer()}else z.__webglFramebuffer=n.createFramebuffer();if(be)for(let se=0,xe=J.length;se<xe;se++){const we=i.get(J[se]);we.__webglTexture===void 0&&(we.__webglTexture=n.createTexture(),o.memory.textures++)}if(R.samples>0&&ve(R)===!1){z.__webglMultisampledFramebuffer=n.createFramebuffer(),z.__webglColorRenderbuffer=[],t.bindFramebuffer(n.FRAMEBUFFER,z.__webglMultisampledFramebuffer);for(let se=0;se<J.length;se++){const xe=J[se];z.__webglColorRenderbuffer[se]=n.createRenderbuffer(),n.bindRenderbuffer(n.RENDERBUFFER,z.__webglColorRenderbuffer[se]);const we=s.convert(xe.format,xe.colorSpace),ie=s.convert(xe.type),de=x(xe.internalFormat,we,ie,xe.colorSpace,R.isXRRenderTarget===!0),Pe=ut(R);n.renderbufferStorageMultisample(n.RENDERBUFFER,Pe,de,R.width,R.height),n.framebufferRenderbuffer(n.FRAMEBUFFER,n.COLOR_ATTACHMENT0+se,n.RENDERBUFFER,z.__webglColorRenderbuffer[se])}n.bindRenderbuffer(n.RENDERBUFFER,null),R.depthBuffer&&(z.__webglDepthRenderbuffer=n.createRenderbuffer(),Le(z.__webglDepthRenderbuffer,R,!0)),t.bindFramebuffer(n.FRAMEBUFFER,null)}}if(q){t.bindTexture(n.TEXTURE_CUBE_MAP,Y.__webglTexture),Ae(n.TEXTURE_CUBE_MAP,E);for(let se=0;se<6;se++)if(E.mipmaps&&E.mipmaps.length>0)for(let xe=0;xe<E.mipmaps.length;xe++)pe(z.__webglFramebuffer[se][xe],R,E,n.COLOR_ATTACHMENT0,n.TEXTURE_CUBE_MAP_POSITIVE_X+se,xe);else pe(z.__webglFramebuffer[se],R,E,n.COLOR_ATTACHMENT0,n.TEXTURE_CUBE_MAP_POSITIVE_X+se,0);m(E)&&h(n.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(be){for(let se=0,xe=J.length;se<xe;se++){const we=J[se],ie=i.get(we);let de=n.TEXTURE_2D;(R.isWebGL3DRenderTarget||R.isWebGLArrayRenderTarget)&&(de=R.isWebGL3DRenderTarget?n.TEXTURE_3D:n.TEXTURE_2D_ARRAY),t.bindTexture(de,ie.__webglTexture),Ae(de,we),pe(z.__webglFramebuffer,R,we,n.COLOR_ATTACHMENT0+se,de,0),m(we)&&h(de)}t.unbindTexture()}else{let se=n.TEXTURE_2D;if((R.isWebGL3DRenderTarget||R.isWebGLArrayRenderTarget)&&(se=R.isWebGL3DRenderTarget?n.TEXTURE_3D:n.TEXTURE_2D_ARRAY),t.bindTexture(se,Y.__webglTexture),Ae(se,E),E.mipmaps&&E.mipmaps.length>0)for(let xe=0;xe<E.mipmaps.length;xe++)pe(z.__webglFramebuffer[xe],R,E,n.COLOR_ATTACHMENT0,se,xe);else pe(z.__webglFramebuffer,R,E,n.COLOR_ATTACHMENT0,se,0);m(E)&&h(se),t.unbindTexture()}R.depthBuffer&&Xe(R)}function ct(R){const E=R.textures;for(let z=0,Y=E.length;z<Y;z++){const J=E[z];if(m(J)){const q=v(R),be=i.get(J).__webglTexture;t.bindTexture(q,be),h(q),t.unbindTexture()}}}const Ue=[],Re=[];function _e(R){if(R.samples>0){if(ve(R)===!1){const E=R.textures,z=R.width,Y=R.height;let J=n.COLOR_BUFFER_BIT;const q=R.stencilBuffer?n.DEPTH_STENCIL_ATTACHMENT:n.DEPTH_ATTACHMENT,be=i.get(R),se=E.length>1;if(se)for(let we=0;we<E.length;we++)t.bindFramebuffer(n.FRAMEBUFFER,be.__webglMultisampledFramebuffer),n.framebufferRenderbuffer(n.FRAMEBUFFER,n.COLOR_ATTACHMENT0+we,n.RENDERBUFFER,null),t.bindFramebuffer(n.FRAMEBUFFER,be.__webglFramebuffer),n.framebufferTexture2D(n.DRAW_FRAMEBUFFER,n.COLOR_ATTACHMENT0+we,n.TEXTURE_2D,null,0);t.bindFramebuffer(n.READ_FRAMEBUFFER,be.__webglMultisampledFramebuffer);const xe=R.texture.mipmaps;xe&&xe.length>0?t.bindFramebuffer(n.DRAW_FRAMEBUFFER,be.__webglFramebuffer[0]):t.bindFramebuffer(n.DRAW_FRAMEBUFFER,be.__webglFramebuffer);for(let we=0;we<E.length;we++){if(R.resolveDepthBuffer&&(R.depthBuffer&&(J|=n.DEPTH_BUFFER_BIT),R.stencilBuffer&&R.resolveStencilBuffer&&(J|=n.STENCIL_BUFFER_BIT)),se){n.framebufferRenderbuffer(n.READ_FRAMEBUFFER,n.COLOR_ATTACHMENT0,n.RENDERBUFFER,be.__webglColorRenderbuffer[we]);const ie=i.get(E[we]).__webglTexture;n.framebufferTexture2D(n.DRAW_FRAMEBUFFER,n.COLOR_ATTACHMENT0,n.TEXTURE_2D,ie,0)}n.blitFramebuffer(0,0,z,Y,0,0,z,Y,J,n.NEAREST),l===!0&&(Ue.length=0,Re.length=0,Ue.push(n.COLOR_ATTACHMENT0+we),R.depthBuffer&&R.resolveDepthBuffer===!1&&(Ue.push(q),Re.push(q),n.invalidateFramebuffer(n.DRAW_FRAMEBUFFER,Re)),n.invalidateFramebuffer(n.READ_FRAMEBUFFER,Ue))}if(t.bindFramebuffer(n.READ_FRAMEBUFFER,null),t.bindFramebuffer(n.DRAW_FRAMEBUFFER,null),se)for(let we=0;we<E.length;we++){t.bindFramebuffer(n.FRAMEBUFFER,be.__webglMultisampledFramebuffer),n.framebufferRenderbuffer(n.FRAMEBUFFER,n.COLOR_ATTACHMENT0+we,n.RENDERBUFFER,be.__webglColorRenderbuffer[we]);const ie=i.get(E[we]).__webglTexture;t.bindFramebuffer(n.FRAMEBUFFER,be.__webglFramebuffer),n.framebufferTexture2D(n.DRAW_FRAMEBUFFER,n.COLOR_ATTACHMENT0+we,n.TEXTURE_2D,ie,0)}t.bindFramebuffer(n.DRAW_FRAMEBUFFER,be.__webglMultisampledFramebuffer)}else if(R.depthBuffer&&R.resolveDepthBuffer===!1&&l){const E=R.stencilBuffer?n.DEPTH_STENCIL_ATTACHMENT:n.DEPTH_ATTACHMENT;n.invalidateFramebuffer(n.DRAW_FRAMEBUFFER,[E])}}}function ut(R){return Math.min(r.maxSamples,R.samples)}function ve(R){const E=i.get(R);return R.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&E.__useRenderToTexture!==!1}function Ne(R){const E=o.render.frame;u.get(R)!==E&&(u.set(R,E),R.update())}function Dt(R,E){const z=R.colorSpace,Y=R.format,J=R.type;return R.isCompressedTexture===!0||R.isVideoTexture===!0||z!==ls&&z!==Pi&&(qe.getTransfer(z)===et?(Y!==Nn||J!==_i)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",z)),E}function vt(R){return typeof HTMLImageElement<"u"&&R instanceof HTMLImageElement?(c.width=R.naturalWidth||R.width,c.height=R.naturalHeight||R.height):typeof VideoFrame<"u"&&R instanceof VideoFrame?(c.width=R.displayWidth,c.height=R.displayHeight):(c.width=R.width,c.height=R.height),c}this.allocateTextureUnit=O,this.resetTextureUnits=D,this.setTexture2D=k,this.setTexture2DArray=G,this.setTexture3D=$,this.setTextureCube=U,this.rebindTextures=Nt,this.setupRenderTarget=L,this.updateRenderTargetMipmap=ct,this.updateMultisampleRenderTarget=_e,this.setupDepthRenderbuffer=Xe,this.setupFrameBufferTexture=pe,this.useMultisampledRTT=ve}function KT(n,e){function t(i,r=Pi){let s;const o=qe.getTransfer(r);if(i===_i)return n.UNSIGNED_BYTE;if(i===Gu)return n.UNSIGNED_SHORT_4_4_4_4;if(i===Wu)return n.UNSIGNED_SHORT_5_5_5_1;if(i===Wp)return n.UNSIGNED_INT_5_9_9_9_REV;if(i===Xp)return n.UNSIGNED_INT_10F_11F_11F_REV;if(i===Hp)return n.BYTE;if(i===Gp)return n.SHORT;if(i===$s)return n.UNSIGNED_SHORT;if(i===Hu)return n.INT;if(i===_r)return n.UNSIGNED_INT;if(i===fi)return n.FLOAT;if(i===go)return n.HALF_FLOAT;if(i===$p)return n.ALPHA;if(i===qp)return n.RGB;if(i===Nn)return n.RGBA;if(i===Ys)return n.DEPTH_COMPONENT;if(i===js)return n.DEPTH_STENCIL;if(i===Yp)return n.RED;if(i===Xu)return n.RED_INTEGER;if(i===jp)return n.RG;if(i===$u)return n.RG_INTEGER;if(i===qu)return n.RGBA_INTEGER;if(i===Qo||i===ea||i===ta||i===na)if(o===et)if(s=e.get("WEBGL_compressed_texture_s3tc_srgb"),s!==null){if(i===Qo)return s.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(i===ea)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(i===ta)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(i===na)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(s=e.get("WEBGL_compressed_texture_s3tc"),s!==null){if(i===Qo)return s.COMPRESSED_RGB_S3TC_DXT1_EXT;if(i===ea)return s.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(i===ta)return s.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(i===na)return s.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(i===bc||i===Sc||i===Ec||i===Mc)if(s=e.get("WEBGL_compressed_texture_pvrtc"),s!==null){if(i===bc)return s.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(i===Sc)return s.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(i===Ec)return s.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(i===Mc)return s.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(i===Tc||i===Ac||i===Cc)if(s=e.get("WEBGL_compressed_texture_etc"),s!==null){if(i===Tc||i===Ac)return o===et?s.COMPRESSED_SRGB8_ETC2:s.COMPRESSED_RGB8_ETC2;if(i===Cc)return o===et?s.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:s.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(i===Pc||i===Rc||i===Dc||i===Lc||i===Ic||i===Uc||i===Oc||i===Fc||i===Nc||i===kc||i===Bc||i===zc||i===Vc||i===Hc)if(s=e.get("WEBGL_compressed_texture_astc"),s!==null){if(i===Pc)return o===et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:s.COMPRESSED_RGBA_ASTC_4x4_KHR;if(i===Rc)return o===et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:s.COMPRESSED_RGBA_ASTC_5x4_KHR;if(i===Dc)return o===et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:s.COMPRESSED_RGBA_ASTC_5x5_KHR;if(i===Lc)return o===et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:s.COMPRESSED_RGBA_ASTC_6x5_KHR;if(i===Ic)return o===et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:s.COMPRESSED_RGBA_ASTC_6x6_KHR;if(i===Uc)return o===et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:s.COMPRESSED_RGBA_ASTC_8x5_KHR;if(i===Oc)return o===et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:s.COMPRESSED_RGBA_ASTC_8x6_KHR;if(i===Fc)return o===et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:s.COMPRESSED_RGBA_ASTC_8x8_KHR;if(i===Nc)return o===et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:s.COMPRESSED_RGBA_ASTC_10x5_KHR;if(i===kc)return o===et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:s.COMPRESSED_RGBA_ASTC_10x6_KHR;if(i===Bc)return o===et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:s.COMPRESSED_RGBA_ASTC_10x8_KHR;if(i===zc)return o===et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:s.COMPRESSED_RGBA_ASTC_10x10_KHR;if(i===Vc)return o===et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:s.COMPRESSED_RGBA_ASTC_12x10_KHR;if(i===Hc)return o===et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:s.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(i===Gc||i===Wc||i===Xc)if(s=e.get("EXT_texture_compression_bptc"),s!==null){if(i===Gc)return o===et?s.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:s.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(i===Wc)return s.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(i===Xc)return s.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(i===$c||i===qc||i===Yc||i===jc)if(s=e.get("EXT_texture_compression_rgtc"),s!==null){if(i===$c)return s.COMPRESSED_RED_RGTC1_EXT;if(i===qc)return s.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(i===Yc)return s.COMPRESSED_RED_GREEN_RGTC2_EXT;if(i===jc)return s.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return i===qs?n.UNSIGNED_INT_24_8:n[i]!==void 0?n[i]:null}return{convert:t}}const ZT=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,JT=`
uniform sampler2DArray depthColor;
uniform float depthWidth;
uniform float depthHeight;

void main() {

	vec2 coord = vec2( gl_FragCoord.x / depthWidth, gl_FragCoord.y / depthHeight );

	if ( coord.x >= 1.0 ) {

		gl_FragDepth = texture( depthColor, vec3( coord.x - 1.0, coord.y, 1 ) ).r;

	} else {

		gl_FragDepth = texture( depthColor, vec3( coord.x, coord.y, 0 ) ).r;

	}

}`;class QT{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t){if(this.texture===null){const i=new um(e.texture);(e.depthNear!==t.depthNear||e.depthFar!==t.depthFar)&&(this.depthNear=e.depthNear,this.depthFar=e.depthFar),this.texture=i}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,i=new ti({vertexShader:ZT,fragmentShader:JT,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new jn(new Va(20,20),i)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class e1 extends Er{constructor(e,t){super();const i=this;let r=null,s=1,o=null,a="local-floor",l=1,c=null,u=null,d=null,p=null,f=null,_=null;const g=typeof XRWebGLBinding<"u",m=new QT,h={},v=t.getContextAttributes();let x=null,w=null;const S=[],C=[],T=new Be;let A=null;const b=new Cn;b.viewport=new yt;const y=new Cn;y.viewport=new yt;const P=[b,y],D=new wb;let O=null,V=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(j){let Q=S[j];return Q===void 0&&(Q=new Ll,S[j]=Q),Q.getTargetRaySpace()},this.getControllerGrip=function(j){let Q=S[j];return Q===void 0&&(Q=new Ll,S[j]=Q),Q.getGripSpace()},this.getHand=function(j){let Q=S[j];return Q===void 0&&(Q=new Ll,S[j]=Q),Q.getHandSpace()};function k(j){const Q=C.indexOf(j.inputSource);if(Q===-1)return;const pe=S[Q];pe!==void 0&&(pe.update(j.inputSource,j.frame,c||o),pe.dispatchEvent({type:j.type,data:j.inputSource}))}function G(){r.removeEventListener("select",k),r.removeEventListener("selectstart",k),r.removeEventListener("selectend",k),r.removeEventListener("squeeze",k),r.removeEventListener("squeezestart",k),r.removeEventListener("squeezeend",k),r.removeEventListener("end",G),r.removeEventListener("inputsourceschange",$);for(let j=0;j<S.length;j++){const Q=C[j];Q!==null&&(C[j]=null,S[j].disconnect(Q))}O=null,V=null,m.reset();for(const j in h)delete h[j];e.setRenderTarget(x),f=null,p=null,d=null,r=null,w=null,ze.stop(),i.isPresenting=!1,e.setPixelRatio(A),e.setSize(T.width,T.height,!1),i.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(j){s=j,i.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(j){a=j,i.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return c||o},this.setReferenceSpace=function(j){c=j},this.getBaseLayer=function(){return p!==null?p:f},this.getBinding=function(){return d===null&&g&&(d=new XRWebGLBinding(r,t)),d},this.getFrame=function(){return _},this.getSession=function(){return r},this.setSession=async function(j){if(r=j,r!==null){if(x=e.getRenderTarget(),r.addEventListener("select",k),r.addEventListener("selectstart",k),r.addEventListener("selectend",k),r.addEventListener("squeeze",k),r.addEventListener("squeezestart",k),r.addEventListener("squeezeend",k),r.addEventListener("end",G),r.addEventListener("inputsourceschange",$),v.xrCompatible!==!0&&await t.makeXRCompatible(),A=e.getPixelRatio(),e.getSize(T),g&&"createProjectionLayer"in XRWebGLBinding.prototype){let pe=null,Le=null,Se=null;v.depth&&(Se=v.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,pe=v.stencil?js:Ys,Le=v.stencil?qs:_r);const Xe={colorFormat:t.RGBA8,depthFormat:Se,scaleFactor:s};d=this.getBinding(),p=d.createProjectionLayer(Xe),r.updateRenderState({layers:[p]}),e.setPixelRatio(1),e.setSize(p.textureWidth,p.textureHeight,!1),w=new xr(p.textureWidth,p.textureHeight,{format:Nn,type:_i,depthTexture:new cm(p.textureWidth,p.textureHeight,Le,void 0,void 0,void 0,void 0,void 0,void 0,pe),stencilBuffer:v.stencil,colorSpace:e.outputColorSpace,samples:v.antialias?4:0,resolveDepthBuffer:p.ignoreDepthValues===!1,resolveStencilBuffer:p.ignoreDepthValues===!1})}else{const pe={antialias:v.antialias,alpha:!0,depth:v.depth,stencil:v.stencil,framebufferScaleFactor:s};f=new XRWebGLLayer(r,t,pe),r.updateRenderState({baseLayer:f}),e.setPixelRatio(1),e.setSize(f.framebufferWidth,f.framebufferHeight,!1),w=new xr(f.framebufferWidth,f.framebufferHeight,{format:Nn,type:_i,colorSpace:e.outputColorSpace,stencilBuffer:v.stencil,resolveDepthBuffer:f.ignoreDepthValues===!1,resolveStencilBuffer:f.ignoreDepthValues===!1})}w.isXRRenderTarget=!0,this.setFoveation(l),c=null,o=await r.requestReferenceSpace(a),ze.setContext(r),ze.start(),i.isPresenting=!0,i.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(r!==null)return r.environmentBlendMode},this.getDepthTexture=function(){return m.getDepthTexture()};function $(j){for(let Q=0;Q<j.removed.length;Q++){const pe=j.removed[Q],Le=C.indexOf(pe);Le>=0&&(C[Le]=null,S[Le].disconnect(pe))}for(let Q=0;Q<j.added.length;Q++){const pe=j.added[Q];let Le=C.indexOf(pe);if(Le===-1){for(let Xe=0;Xe<S.length;Xe++)if(Xe>=C.length){C.push(pe),Le=Xe;break}else if(C[Xe]===null){C[Xe]=pe,Le=Xe;break}if(Le===-1)break}const Se=S[Le];Se&&Se.connect(pe)}}const U=new B,Z=new B;function ee(j,Q,pe){U.setFromMatrixPosition(Q.matrixWorld),Z.setFromMatrixPosition(pe.matrixWorld);const Le=U.distanceTo(Z),Se=Q.projectionMatrix.elements,Xe=pe.projectionMatrix.elements,Nt=Se[14]/(Se[10]-1),L=Se[14]/(Se[10]+1),ct=(Se[9]+1)/Se[5],Ue=(Se[9]-1)/Se[5],Re=(Se[8]-1)/Se[0],_e=(Xe[8]+1)/Xe[0],ut=Nt*Re,ve=Nt*_e,Ne=Le/(-Re+_e),Dt=Ne*-Re;if(Q.matrixWorld.decompose(j.position,j.quaternion,j.scale),j.translateX(Dt),j.translateZ(Ne),j.matrixWorld.compose(j.position,j.quaternion,j.scale),j.matrixWorldInverse.copy(j.matrixWorld).invert(),Se[10]===-1)j.projectionMatrix.copy(Q.projectionMatrix),j.projectionMatrixInverse.copy(Q.projectionMatrixInverse);else{const vt=Nt+Ne,R=L+Ne,E=ut-Dt,z=ve+(Le-Dt),Y=ct*L/R*vt,J=Ue*L/R*vt;j.projectionMatrix.makePerspective(E,z,Y,J,vt,R),j.projectionMatrixInverse.copy(j.projectionMatrix).invert()}}function ce(j,Q){Q===null?j.matrixWorld.copy(j.matrix):j.matrixWorld.multiplyMatrices(Q.matrixWorld,j.matrix),j.matrixWorldInverse.copy(j.matrixWorld).invert()}this.updateCamera=function(j){if(r===null)return;let Q=j.near,pe=j.far;m.texture!==null&&(m.depthNear>0&&(Q=m.depthNear),m.depthFar>0&&(pe=m.depthFar)),D.near=y.near=b.near=Q,D.far=y.far=b.far=pe,(O!==D.near||V!==D.far)&&(r.updateRenderState({depthNear:D.near,depthFar:D.far}),O=D.near,V=D.far),D.layers.mask=j.layers.mask|6,b.layers.mask=D.layers.mask&3,y.layers.mask=D.layers.mask&5;const Le=j.parent,Se=D.cameras;ce(D,Le);for(let Xe=0;Xe<Se.length;Xe++)ce(Se[Xe],Le);Se.length===2?ee(D,b,y):D.projectionMatrix.copy(b.projectionMatrix),Ae(j,D,Le)};function Ae(j,Q,pe){pe===null?j.matrix.copy(Q.matrixWorld):(j.matrix.copy(pe.matrixWorld),j.matrix.invert(),j.matrix.multiply(Q.matrixWorld)),j.matrix.decompose(j.position,j.quaternion,j.scale),j.updateMatrixWorld(!0),j.projectionMatrix.copy(Q.projectionMatrix),j.projectionMatrixInverse.copy(Q.projectionMatrixInverse),j.isPerspectiveCamera&&(j.fov=Ks*2*Math.atan(1/j.projectionMatrix.elements[5]),j.zoom=1)}this.getCamera=function(){return D},this.getFoveation=function(){if(!(p===null&&f===null))return l},this.setFoveation=function(j){l=j,p!==null&&(p.fixedFoveation=j),f!==null&&f.fixedFoveation!==void 0&&(f.fixedFoveation=j)},this.hasDepthSensing=function(){return m.texture!==null},this.getDepthSensingMesh=function(){return m.getMesh(D)},this.getCameraTexture=function(j){return h[j]};let Je=null;function We(j,Q){if(u=Q.getViewerPose(c||o),_=Q,u!==null){const pe=u.views;f!==null&&(e.setRenderTargetFramebuffer(w,f.framebuffer),e.setRenderTarget(w));let Le=!1;pe.length!==D.cameras.length&&(D.cameras.length=0,Le=!0);for(let L=0;L<pe.length;L++){const ct=pe[L];let Ue=null;if(f!==null)Ue=f.getViewport(ct);else{const _e=d.getViewSubImage(p,ct);Ue=_e.viewport,L===0&&(e.setRenderTargetTextures(w,_e.colorTexture,_e.depthStencilTexture),e.setRenderTarget(w))}let Re=P[L];Re===void 0&&(Re=new Cn,Re.layers.enable(L),Re.viewport=new yt,P[L]=Re),Re.matrix.fromArray(ct.transform.matrix),Re.matrix.decompose(Re.position,Re.quaternion,Re.scale),Re.projectionMatrix.fromArray(ct.projectionMatrix),Re.projectionMatrixInverse.copy(Re.projectionMatrix).invert(),Re.viewport.set(Ue.x,Ue.y,Ue.width,Ue.height),L===0&&(D.matrix.copy(Re.matrix),D.matrix.decompose(D.position,D.quaternion,D.scale)),Le===!0&&D.cameras.push(Re)}const Se=r.enabledFeatures;if(Se&&Se.includes("depth-sensing")&&r.depthUsage=="gpu-optimized"&&g){d=i.getBinding();const L=d.getDepthInformation(pe[0]);L&&L.isValid&&L.texture&&m.init(L,r.renderState)}if(Se&&Se.includes("camera-access")&&g){e.state.unbindTexture(),d=i.getBinding();for(let L=0;L<pe.length;L++){const ct=pe[L].camera;if(ct){let Ue=h[ct];Ue||(Ue=new um,h[ct]=Ue);const Re=d.getCameraImage(ct);Ue.sourceTexture=Re}}}}for(let pe=0;pe<S.length;pe++){const Le=C[pe],Se=S[pe];Le!==null&&Se!==void 0&&Se.update(Le,Q,c||o)}Je&&Je(j,Q),Q.detectedPlanes&&i.dispatchEvent({type:"planesdetected",data:Q}),_=null}const ze=new dm;ze.setAnimationLoop(We),this.setAnimationLoop=function(j){Je=j},this.dispose=function(){}}}const er=new vi,t1=new Tt;function n1(n,e){function t(m,h){m.matrixAutoUpdate===!0&&m.updateMatrix(),h.value.copy(m.matrix)}function i(m,h){h.color.getRGB(m.fogColor.value,rm(n)),h.isFog?(m.fogNear.value=h.near,m.fogFar.value=h.far):h.isFogExp2&&(m.fogDensity.value=h.density)}function r(m,h,v,x,w){h.isMeshBasicMaterial||h.isMeshLambertMaterial?s(m,h):h.isMeshToonMaterial?(s(m,h),d(m,h)):h.isMeshPhongMaterial?(s(m,h),u(m,h)):h.isMeshStandardMaterial?(s(m,h),p(m,h),h.isMeshPhysicalMaterial&&f(m,h,w)):h.isMeshMatcapMaterial?(s(m,h),_(m,h)):h.isMeshDepthMaterial?s(m,h):h.isMeshDistanceMaterial?(s(m,h),g(m,h)):h.isMeshNormalMaterial?s(m,h):h.isLineBasicMaterial?(o(m,h),h.isLineDashedMaterial&&a(m,h)):h.isPointsMaterial?l(m,h,v,x):h.isSpriteMaterial?c(m,h):h.isShadowMaterial?(m.color.value.copy(h.color),m.opacity.value=h.opacity):h.isShaderMaterial&&(h.uniformsNeedUpdate=!1)}function s(m,h){m.opacity.value=h.opacity,h.color&&m.diffuse.value.copy(h.color),h.emissive&&m.emissive.value.copy(h.emissive).multiplyScalar(h.emissiveIntensity),h.map&&(m.map.value=h.map,t(h.map,m.mapTransform)),h.alphaMap&&(m.alphaMap.value=h.alphaMap,t(h.alphaMap,m.alphaMapTransform)),h.bumpMap&&(m.bumpMap.value=h.bumpMap,t(h.bumpMap,m.bumpMapTransform),m.bumpScale.value=h.bumpScale,h.side===qt&&(m.bumpScale.value*=-1)),h.normalMap&&(m.normalMap.value=h.normalMap,t(h.normalMap,m.normalMapTransform),m.normalScale.value.copy(h.normalScale),h.side===qt&&m.normalScale.value.negate()),h.displacementMap&&(m.displacementMap.value=h.displacementMap,t(h.displacementMap,m.displacementMapTransform),m.displacementScale.value=h.displacementScale,m.displacementBias.value=h.displacementBias),h.emissiveMap&&(m.emissiveMap.value=h.emissiveMap,t(h.emissiveMap,m.emissiveMapTransform)),h.specularMap&&(m.specularMap.value=h.specularMap,t(h.specularMap,m.specularMapTransform)),h.alphaTest>0&&(m.alphaTest.value=h.alphaTest);const v=e.get(h),x=v.envMap,w=v.envMapRotation;x&&(m.envMap.value=x,er.copy(w),er.x*=-1,er.y*=-1,er.z*=-1,x.isCubeTexture&&x.isRenderTargetTexture===!1&&(er.y*=-1,er.z*=-1),m.envMapRotation.value.setFromMatrix4(t1.makeRotationFromEuler(er)),m.flipEnvMap.value=x.isCubeTexture&&x.isRenderTargetTexture===!1?-1:1,m.reflectivity.value=h.reflectivity,m.ior.value=h.ior,m.refractionRatio.value=h.refractionRatio),h.lightMap&&(m.lightMap.value=h.lightMap,m.lightMapIntensity.value=h.lightMapIntensity,t(h.lightMap,m.lightMapTransform)),h.aoMap&&(m.aoMap.value=h.aoMap,m.aoMapIntensity.value=h.aoMapIntensity,t(h.aoMap,m.aoMapTransform))}function o(m,h){m.diffuse.value.copy(h.color),m.opacity.value=h.opacity,h.map&&(m.map.value=h.map,t(h.map,m.mapTransform))}function a(m,h){m.dashSize.value=h.dashSize,m.totalSize.value=h.dashSize+h.gapSize,m.scale.value=h.scale}function l(m,h,v,x){m.diffuse.value.copy(h.color),m.opacity.value=h.opacity,m.size.value=h.size*v,m.scale.value=x*.5,h.map&&(m.map.value=h.map,t(h.map,m.uvTransform)),h.alphaMap&&(m.alphaMap.value=h.alphaMap,t(h.alphaMap,m.alphaMapTransform)),h.alphaTest>0&&(m.alphaTest.value=h.alphaTest)}function c(m,h){m.diffuse.value.copy(h.color),m.opacity.value=h.opacity,m.rotation.value=h.rotation,h.map&&(m.map.value=h.map,t(h.map,m.mapTransform)),h.alphaMap&&(m.alphaMap.value=h.alphaMap,t(h.alphaMap,m.alphaMapTransform)),h.alphaTest>0&&(m.alphaTest.value=h.alphaTest)}function u(m,h){m.specular.value.copy(h.specular),m.shininess.value=Math.max(h.shininess,1e-4)}function d(m,h){h.gradientMap&&(m.gradientMap.value=h.gradientMap)}function p(m,h){m.metalness.value=h.metalness,h.metalnessMap&&(m.metalnessMap.value=h.metalnessMap,t(h.metalnessMap,m.metalnessMapTransform)),m.roughness.value=h.roughness,h.roughnessMap&&(m.roughnessMap.value=h.roughnessMap,t(h.roughnessMap,m.roughnessMapTransform)),h.envMap&&(m.envMapIntensity.value=h.envMapIntensity)}function f(m,h,v){m.ior.value=h.ior,h.sheen>0&&(m.sheenColor.value.copy(h.sheenColor).multiplyScalar(h.sheen),m.sheenRoughness.value=h.sheenRoughness,h.sheenColorMap&&(m.sheenColorMap.value=h.sheenColorMap,t(h.sheenColorMap,m.sheenColorMapTransform)),h.sheenRoughnessMap&&(m.sheenRoughnessMap.value=h.sheenRoughnessMap,t(h.sheenRoughnessMap,m.sheenRoughnessMapTransform))),h.clearcoat>0&&(m.clearcoat.value=h.clearcoat,m.clearcoatRoughness.value=h.clearcoatRoughness,h.clearcoatMap&&(m.clearcoatMap.value=h.clearcoatMap,t(h.clearcoatMap,m.clearcoatMapTransform)),h.clearcoatRoughnessMap&&(m.clearcoatRoughnessMap.value=h.clearcoatRoughnessMap,t(h.clearcoatRoughnessMap,m.clearcoatRoughnessMapTransform)),h.clearcoatNormalMap&&(m.clearcoatNormalMap.value=h.clearcoatNormalMap,t(h.clearcoatNormalMap,m.clearcoatNormalMapTransform),m.clearcoatNormalScale.value.copy(h.clearcoatNormalScale),h.side===qt&&m.clearcoatNormalScale.value.negate())),h.dispersion>0&&(m.dispersion.value=h.dispersion),h.iridescence>0&&(m.iridescence.value=h.iridescence,m.iridescenceIOR.value=h.iridescenceIOR,m.iridescenceThicknessMinimum.value=h.iridescenceThicknessRange[0],m.iridescenceThicknessMaximum.value=h.iridescenceThicknessRange[1],h.iridescenceMap&&(m.iridescenceMap.value=h.iridescenceMap,t(h.iridescenceMap,m.iridescenceMapTransform)),h.iridescenceThicknessMap&&(m.iridescenceThicknessMap.value=h.iridescenceThicknessMap,t(h.iridescenceThicknessMap,m.iridescenceThicknessMapTransform))),h.transmission>0&&(m.transmission.value=h.transmission,m.transmissionSamplerMap.value=v.texture,m.transmissionSamplerSize.value.set(v.width,v.height),h.transmissionMap&&(m.transmissionMap.value=h.transmissionMap,t(h.transmissionMap,m.transmissionMapTransform)),m.thickness.value=h.thickness,h.thicknessMap&&(m.thicknessMap.value=h.thicknessMap,t(h.thicknessMap,m.thicknessMapTransform)),m.attenuationDistance.value=h.attenuationDistance,m.attenuationColor.value.copy(h.attenuationColor)),h.anisotropy>0&&(m.anisotropyVector.value.set(h.anisotropy*Math.cos(h.anisotropyRotation),h.anisotropy*Math.sin(h.anisotropyRotation)),h.anisotropyMap&&(m.anisotropyMap.value=h.anisotropyMap,t(h.anisotropyMap,m.anisotropyMapTransform))),m.specularIntensity.value=h.specularIntensity,m.specularColor.value.copy(h.specularColor),h.specularColorMap&&(m.specularColorMap.value=h.specularColorMap,t(h.specularColorMap,m.specularColorMapTransform)),h.specularIntensityMap&&(m.specularIntensityMap.value=h.specularIntensityMap,t(h.specularIntensityMap,m.specularIntensityMapTransform))}function _(m,h){h.matcap&&(m.matcap.value=h.matcap)}function g(m,h){const v=e.get(h).light;m.referencePosition.value.setFromMatrixPosition(v.matrixWorld),m.nearDistance.value=v.shadow.camera.near,m.farDistance.value=v.shadow.camera.far}return{refreshFogUniforms:i,refreshMaterialUniforms:r}}function i1(n,e,t,i){let r={},s={},o=[];const a=n.getParameter(n.MAX_UNIFORM_BUFFER_BINDINGS);function l(v,x){const w=x.program;i.uniformBlockBinding(v,w)}function c(v,x){let w=r[v.id];w===void 0&&(_(v),w=u(v),r[v.id]=w,v.addEventListener("dispose",m));const S=x.program;i.updateUBOMapping(v,S);const C=e.render.frame;s[v.id]!==C&&(p(v),s[v.id]=C)}function u(v){const x=d();v.__bindingPointIndex=x;const w=n.createBuffer(),S=v.__size,C=v.usage;return n.bindBuffer(n.UNIFORM_BUFFER,w),n.bufferData(n.UNIFORM_BUFFER,S,C),n.bindBuffer(n.UNIFORM_BUFFER,null),n.bindBufferBase(n.UNIFORM_BUFFER,x,w),w}function d(){for(let v=0;v<a;v++)if(o.indexOf(v)===-1)return o.push(v),v;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function p(v){const x=r[v.id],w=v.uniforms,S=v.__cache;n.bindBuffer(n.UNIFORM_BUFFER,x);for(let C=0,T=w.length;C<T;C++){const A=Array.isArray(w[C])?w[C]:[w[C]];for(let b=0,y=A.length;b<y;b++){const P=A[b];if(f(P,C,b,S)===!0){const D=P.__offset,O=Array.isArray(P.value)?P.value:[P.value];let V=0;for(let k=0;k<O.length;k++){const G=O[k],$=g(G);typeof G=="number"||typeof G=="boolean"?(P.__data[0]=G,n.bufferSubData(n.UNIFORM_BUFFER,D+V,P.__data)):G.isMatrix3?(P.__data[0]=G.elements[0],P.__data[1]=G.elements[1],P.__data[2]=G.elements[2],P.__data[3]=0,P.__data[4]=G.elements[3],P.__data[5]=G.elements[4],P.__data[6]=G.elements[5],P.__data[7]=0,P.__data[8]=G.elements[6],P.__data[9]=G.elements[7],P.__data[10]=G.elements[8],P.__data[11]=0):(G.toArray(P.__data,V),V+=$.storage/Float32Array.BYTES_PER_ELEMENT)}n.bufferSubData(n.UNIFORM_BUFFER,D,P.__data)}}}n.bindBuffer(n.UNIFORM_BUFFER,null)}function f(v,x,w,S){const C=v.value,T=x+"_"+w;if(S[T]===void 0)return typeof C=="number"||typeof C=="boolean"?S[T]=C:S[T]=C.clone(),!0;{const A=S[T];if(typeof C=="number"||typeof C=="boolean"){if(A!==C)return S[T]=C,!0}else if(A.equals(C)===!1)return A.copy(C),!0}return!1}function _(v){const x=v.uniforms;let w=0;const S=16;for(let T=0,A=x.length;T<A;T++){const b=Array.isArray(x[T])?x[T]:[x[T]];for(let y=0,P=b.length;y<P;y++){const D=b[y],O=Array.isArray(D.value)?D.value:[D.value];for(let V=0,k=O.length;V<k;V++){const G=O[V],$=g(G),U=w%S,Z=U%$.boundary,ee=U+Z;w+=Z,ee!==0&&S-ee<$.storage&&(w+=S-ee),D.__data=new Float32Array($.storage/Float32Array.BYTES_PER_ELEMENT),D.__offset=w,w+=$.storage}}}const C=w%S;return C>0&&(w+=S-C),v.__size=w,v.__cache={},this}function g(v){const x={boundary:0,storage:0};return typeof v=="number"||typeof v=="boolean"?(x.boundary=4,x.storage=4):v.isVector2?(x.boundary=8,x.storage=8):v.isVector3||v.isColor?(x.boundary=16,x.storage=12):v.isVector4?(x.boundary=16,x.storage=16):v.isMatrix3?(x.boundary=48,x.storage=48):v.isMatrix4?(x.boundary=64,x.storage=64):v.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",v),x}function m(v){const x=v.target;x.removeEventListener("dispose",m);const w=o.indexOf(x.__bindingPointIndex);o.splice(w,1),n.deleteBuffer(r[x.id]),delete r[x.id],delete s[x.id]}function h(){for(const v in r)n.deleteBuffer(r[v]);o=[],r={},s={}}return{bind:l,update:c,dispose:h}}class r1{constructor(e={}){const{canvas:t=Fy(),context:i=null,depth:r=!0,stencil:s=!1,alpha:o=!1,antialias:a=!1,premultipliedAlpha:l=!0,preserveDrawingBuffer:c=!1,powerPreference:u="default",failIfMajorPerformanceCaveat:d=!1,reversedDepthBuffer:p=!1}=e;this.isWebGLRenderer=!0;let f;if(i!==null){if(typeof WebGLRenderingContext<"u"&&i instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");f=i.getContextAttributes().alpha}else f=o;const _=new Uint32Array(4),g=new Int32Array(4);let m=null,h=null;const v=[],x=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this.toneMapping=Bi,this.toneMappingExposure=1,this.transmissionResolutionScale=1;const w=this;let S=!1;this._outputColorSpace=An;let C=0,T=0,A=null,b=-1,y=null;const P=new yt,D=new yt;let O=null;const V=new Ze(0);let k=0,G=t.width,$=t.height,U=1,Z=null,ee=null;const ce=new yt(0,0,G,$),Ae=new yt(0,0,G,$);let Je=!1;const We=new lm;let ze=!1,j=!1;const Q=new Tt,pe=new B,Le=new yt,Se={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let Xe=!1;function Nt(){return A===null?U:1}let L=i;function ct(M,F){return t.getContext(M,F)}try{const M={alpha:!0,depth:r,stencil:s,antialias:a,premultipliedAlpha:l,preserveDrawingBuffer:c,powerPreference:u,failIfMajorPerformanceCaveat:d};if("setAttribute"in t&&t.setAttribute("data-engine",`three.js r${Vu}`),t.addEventListener("webglcontextlost",oe,!1),t.addEventListener("webglcontextrestored",fe,!1),t.addEventListener("webglcontextcreationerror",te,!1),L===null){const F="webgl2";if(L=ct(F,M),L===null)throw ct(F)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(M){throw console.error("THREE.WebGLRenderer: "+M.message),M}let Ue,Re,_e,ut,ve,Ne,Dt,vt,R,E,z,Y,J,q,be,se,xe,we,ie,de,Pe,ye,le,Oe;function I(){Ue=new pM(L),Ue.init(),ye=new KT(L,Ue),Re=new aM(L,Ue,e,ye),_e=new YT(L,Ue),Re.reversedDepthBuffer&&p&&_e.buffers.depth.setReversed(!0),ut=new _M(L),ve=new OT,Ne=new jT(L,Ue,_e,ve,Re,ye,ut),Dt=new cM(w),vt=new fM(w),R=new Sb(L),le=new sM(L,R),E=new mM(L,R,ut,le),z=new xM(L,E,R,ut),ie=new vM(L,Re,Ne),se=new lM(ve),Y=new UT(w,Dt,vt,Ue,Re,le,se),J=new n1(w,ve),q=new NT,be=new GT(Ue),we=new rM(w,Dt,vt,_e,z,f,l),xe=new $T(w,z,Re),Oe=new i1(L,ut,Re,_e),de=new oM(L,Ue,ut),Pe=new gM(L,Ue,ut),ut.programs=Y.programs,w.capabilities=Re,w.extensions=Ue,w.properties=ve,w.renderLists=q,w.shadowMap=xe,w.state=_e,w.info=ut}I();const re=new e1(w,L);this.xr=re,this.getContext=function(){return L},this.getContextAttributes=function(){return L.getContextAttributes()},this.forceContextLoss=function(){const M=Ue.get("WEBGL_lose_context");M&&M.loseContext()},this.forceContextRestore=function(){const M=Ue.get("WEBGL_lose_context");M&&M.restoreContext()},this.getPixelRatio=function(){return U},this.setPixelRatio=function(M){M!==void 0&&(U=M,this.setSize(G,$,!1))},this.getSize=function(M){return M.set(G,$)},this.setSize=function(M,F,H=!0){if(re.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}G=M,$=F,t.width=Math.floor(M*U),t.height=Math.floor(F*U),H===!0&&(t.style.width=M+"px",t.style.height=F+"px"),this.setViewport(0,0,M,F)},this.getDrawingBufferSize=function(M){return M.set(G*U,$*U).floor()},this.setDrawingBufferSize=function(M,F,H){G=M,$=F,U=H,t.width=Math.floor(M*H),t.height=Math.floor(F*H),this.setViewport(0,0,M,F)},this.getCurrentViewport=function(M){return M.copy(P)},this.getViewport=function(M){return M.copy(ce)},this.setViewport=function(M,F,H,W){M.isVector4?ce.set(M.x,M.y,M.z,M.w):ce.set(M,F,H,W),_e.viewport(P.copy(ce).multiplyScalar(U).round())},this.getScissor=function(M){return M.copy(Ae)},this.setScissor=function(M,F,H,W){M.isVector4?Ae.set(M.x,M.y,M.z,M.w):Ae.set(M,F,H,W),_e.scissor(D.copy(Ae).multiplyScalar(U).round())},this.getScissorTest=function(){return Je},this.setScissorTest=function(M){_e.setScissorTest(Je=M)},this.setOpaqueSort=function(M){Z=M},this.setTransparentSort=function(M){ee=M},this.getClearColor=function(M){return M.copy(we.getClearColor())},this.setClearColor=function(){we.setClearColor(...arguments)},this.getClearAlpha=function(){return we.getClearAlpha()},this.setClearAlpha=function(){we.setClearAlpha(...arguments)},this.clear=function(M=!0,F=!0,H=!0){let W=0;if(M){let N=!1;if(A!==null){const ne=A.texture.format;N=ne===qu||ne===$u||ne===Xu}if(N){const ne=A.texture.type,ue=ne===_i||ne===_r||ne===$s||ne===qs||ne===Gu||ne===Wu,me=we.getClearColor(),he=we.getClearAlpha(),Ce=me.r,De=me.g,Ee=me.b;ue?(_[0]=Ce,_[1]=De,_[2]=Ee,_[3]=he,L.clearBufferuiv(L.COLOR,0,_)):(g[0]=Ce,g[1]=De,g[2]=Ee,g[3]=he,L.clearBufferiv(L.COLOR,0,g))}else W|=L.COLOR_BUFFER_BIT}F&&(W|=L.DEPTH_BUFFER_BIT),H&&(W|=L.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),L.clear(W)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",oe,!1),t.removeEventListener("webglcontextrestored",fe,!1),t.removeEventListener("webglcontextcreationerror",te,!1),we.dispose(),q.dispose(),be.dispose(),ve.dispose(),Dt.dispose(),vt.dispose(),z.dispose(),le.dispose(),Oe.dispose(),Y.dispose(),re.dispose(),re.removeEventListener("sessionstart",zn),re.removeEventListener("sessionend",xd),$i.stop()};function oe(M){M.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),S=!0}function fe(){console.log("THREE.WebGLRenderer: Context Restored."),S=!1;const M=ut.autoReset,F=xe.enabled,H=xe.autoUpdate,W=xe.needsUpdate,N=xe.type;I(),ut.autoReset=M,xe.enabled=F,xe.autoUpdate=H,xe.needsUpdate=W,xe.type=N}function te(M){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",M.statusMessage)}function K(M){const F=M.target;F.removeEventListener("dispose",K),ge(F)}function ge(M){Ie(M),ve.remove(M)}function Ie(M){const F=ve.get(M).programs;F!==void 0&&(F.forEach(function(H){Y.releaseProgram(H)}),M.isShaderMaterial&&Y.releaseShaderCache(M))}this.renderBufferDirect=function(M,F,H,W,N,ne){F===null&&(F=Se);const ue=N.isMesh&&N.matrixWorld.determinant()<0,me=_g(M,F,H,W,N);_e.setMaterial(W,ue);let he=H.index,Ce=1;if(W.wireframe===!0){if(he=E.getWireframeAttribute(H),he===void 0)return;Ce=2}const De=H.drawRange,Ee=H.attributes.position;let He=De.start*Ce,Qe=(De.start+De.count)*Ce;ne!==null&&(He=Math.max(He,ne.start*Ce),Qe=Math.min(Qe,(ne.start+ne.count)*Ce)),he!==null?(He=Math.max(He,0),Qe=Math.min(Qe,he.count)):Ee!=null&&(He=Math.max(He,0),Qe=Math.min(Qe,Ee.count));const gt=Qe-He;if(gt<0||gt===1/0)return;le.setup(N,W,me,H,he);let at,nt=de;if(he!==null&&(at=R.get(he),nt=Pe,nt.setIndex(at)),N.isMesh)W.wireframe===!0?(_e.setLineWidth(W.wireframeLinewidth*Nt()),nt.setMode(L.LINES)):nt.setMode(L.TRIANGLES);else if(N.isLine){let Te=W.linewidth;Te===void 0&&(Te=1),_e.setLineWidth(Te*Nt()),N.isLineSegments?nt.setMode(L.LINES):N.isLineLoop?nt.setMode(L.LINE_LOOP):nt.setMode(L.LINE_STRIP)}else N.isPoints?nt.setMode(L.POINTS):N.isSprite&&nt.setMode(L.TRIANGLES);if(N.isBatchedMesh)if(N._multiDrawInstances!==null)Js("THREE.WebGLRenderer: renderMultiDrawInstances has been deprecated and will be removed in r184. Append to renderMultiDraw arguments and use indirection."),nt.renderMultiDrawInstances(N._multiDrawStarts,N._multiDrawCounts,N._multiDrawCount,N._multiDrawInstances);else if(Ue.get("WEBGL_multi_draw"))nt.renderMultiDraw(N._multiDrawStarts,N._multiDrawCounts,N._multiDrawCount);else{const Te=N._multiDrawStarts,ht=N._multiDrawCounts,$e=N._multiDrawCount,ln=he?R.get(he).bytesPerElement:1,Tr=ve.get(W).currentProgram.getUniforms();for(let cn=0;cn<$e;cn++)Tr.setValue(L,"_gl_DrawID",cn),nt.render(Te[cn]/ln,ht[cn])}else if(N.isInstancedMesh)nt.renderInstances(He,gt,N.count);else if(H.isInstancedBufferGeometry){const Te=H._maxInstanceCount!==void 0?H._maxInstanceCount:1/0,ht=Math.min(H.instanceCount,Te);nt.renderInstances(He,gt,ht)}else nt.render(He,gt)};function st(M,F,H){M.transparent===!0&&M.side===hi&&M.forceSinglePass===!1?(M.side=qt,M.needsUpdate=!0,yo(M,F,H),M.side=Hi,M.needsUpdate=!0,yo(M,F,H),M.side=hi):yo(M,F,H)}this.compile=function(M,F,H=null){H===null&&(H=M),h=be.get(H),h.init(F),x.push(h),H.traverseVisible(function(N){N.isLight&&N.layers.test(F.layers)&&(h.pushLight(N),N.castShadow&&h.pushShadow(N))}),M!==H&&M.traverseVisible(function(N){N.isLight&&N.layers.test(F.layers)&&(h.pushLight(N),N.castShadow&&h.pushShadow(N))}),h.setupLights();const W=new Set;return M.traverse(function(N){if(!(N.isMesh||N.isPoints||N.isLine||N.isSprite))return;const ne=N.material;if(ne)if(Array.isArray(ne))for(let ue=0;ue<ne.length;ue++){const me=ne[ue];st(me,H,N),W.add(me)}else st(ne,H,N),W.add(ne)}),h=x.pop(),W},this.compileAsync=function(M,F,H=null){const W=this.compile(M,F,H);return new Promise(N=>{function ne(){if(W.forEach(function(ue){ve.get(ue).currentProgram.isReady()&&W.delete(ue)}),W.size===0){N(M);return}setTimeout(ne,10)}Ue.get("KHR_parallel_shader_compile")!==null?ne():setTimeout(ne,10)})};let Ke=null;function ii(M){Ke&&Ke(M)}function zn(){$i.stop()}function xd(){$i.start()}const $i=new dm;$i.setAnimationLoop(ii),typeof self<"u"&&$i.setContext(self),this.setAnimationLoop=function(M){Ke=M,re.setAnimationLoop(M),M===null?$i.stop():$i.start()},re.addEventListener("sessionstart",zn),re.addEventListener("sessionend",xd),this.render=function(M,F){if(F!==void 0&&F.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(S===!0)return;if(M.matrixWorldAutoUpdate===!0&&M.updateMatrixWorld(),F.parent===null&&F.matrixWorldAutoUpdate===!0&&F.updateMatrixWorld(),re.enabled===!0&&re.isPresenting===!0&&(re.cameraAutoUpdate===!0&&re.updateCamera(F),F=re.getCamera()),M.isScene===!0&&M.onBeforeRender(w,M,F,A),h=be.get(M,x.length),h.init(F),x.push(h),Q.multiplyMatrices(F.projectionMatrix,F.matrixWorldInverse),We.setFromProjectionMatrix(Q,Yn,F.reversedDepth),j=this.localClippingEnabled,ze=se.init(this.clippingPlanes,j),m=q.get(M,v.length),m.init(),v.push(m),re.enabled===!0&&re.isPresenting===!0){const ne=w.xr.getDepthSensingMesh();ne!==null&&qa(ne,F,-1/0,w.sortObjects)}qa(M,F,0,w.sortObjects),m.finish(),w.sortObjects===!0&&m.sort(Z,ee),Xe=re.enabled===!1||re.isPresenting===!1||re.hasDepthSensing()===!1,Xe&&we.addToRenderList(m,M),this.info.render.frame++,ze===!0&&se.beginShadows();const H=h.state.shadowsArray;xe.render(H,M,F),ze===!0&&se.endShadows(),this.info.autoReset===!0&&this.info.reset();const W=m.opaque,N=m.transmissive;if(h.setupLights(),F.isArrayCamera){const ne=F.cameras;if(N.length>0)for(let ue=0,me=ne.length;ue<me;ue++){const he=ne[ue];yd(W,N,M,he)}Xe&&we.render(M);for(let ue=0,me=ne.length;ue<me;ue++){const he=ne[ue];wd(m,M,he,he.viewport)}}else N.length>0&&yd(W,N,M,F),Xe&&we.render(M),wd(m,M,F);A!==null&&T===0&&(Ne.updateMultisampleRenderTarget(A),Ne.updateRenderTargetMipmap(A)),M.isScene===!0&&M.onAfterRender(w,M,F),le.resetDefaultState(),b=-1,y=null,x.pop(),x.length>0?(h=x[x.length-1],ze===!0&&se.setGlobalState(w.clippingPlanes,h.state.camera)):h=null,v.pop(),v.length>0?m=v[v.length-1]:m=null};function qa(M,F,H,W){if(M.visible===!1)return;if(M.layers.test(F.layers)){if(M.isGroup)H=M.renderOrder;else if(M.isLOD)M.autoUpdate===!0&&M.update(F);else if(M.isLight)h.pushLight(M),M.castShadow&&h.pushShadow(M);else if(M.isSprite){if(!M.frustumCulled||We.intersectsSprite(M)){W&&Le.setFromMatrixPosition(M.matrixWorld).applyMatrix4(Q);const ue=z.update(M),me=M.material;me.visible&&m.push(M,ue,me,H,Le.z,null)}}else if((M.isMesh||M.isLine||M.isPoints)&&(!M.frustumCulled||We.intersectsObject(M))){const ue=z.update(M),me=M.material;if(W&&(M.boundingSphere!==void 0?(M.boundingSphere===null&&M.computeBoundingSphere(),Le.copy(M.boundingSphere.center)):(ue.boundingSphere===null&&ue.computeBoundingSphere(),Le.copy(ue.boundingSphere.center)),Le.applyMatrix4(M.matrixWorld).applyMatrix4(Q)),Array.isArray(me)){const he=ue.groups;for(let Ce=0,De=he.length;Ce<De;Ce++){const Ee=he[Ce],He=me[Ee.materialIndex];He&&He.visible&&m.push(M,ue,He,H,Le.z,Ee)}}else me.visible&&m.push(M,ue,me,H,Le.z,null)}}const ne=M.children;for(let ue=0,me=ne.length;ue<me;ue++)qa(ne[ue],F,H,W)}function wd(M,F,H,W){const N=M.opaque,ne=M.transmissive,ue=M.transparent;h.setupLightsView(H),ze===!0&&se.setGlobalState(w.clippingPlanes,H),W&&_e.viewport(P.copy(W)),N.length>0&&wo(N,F,H),ne.length>0&&wo(ne,F,H),ue.length>0&&wo(ue,F,H),_e.buffers.depth.setTest(!0),_e.buffers.depth.setMask(!0),_e.buffers.color.setMask(!0),_e.setPolygonOffset(!1)}function yd(M,F,H,W){if((H.isScene===!0?H.overrideMaterial:null)!==null)return;h.state.transmissionRenderTarget[W.id]===void 0&&(h.state.transmissionRenderTarget[W.id]=new xr(1,1,{generateMipmaps:!0,type:Ue.has("EXT_color_buffer_half_float")||Ue.has("EXT_color_buffer_float")?go:_i,minFilter:cr,samples:4,stencilBuffer:s,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:qe.workingColorSpace}));const ne=h.state.transmissionRenderTarget[W.id],ue=W.viewport||P;ne.setSize(ue.z*w.transmissionResolutionScale,ue.w*w.transmissionResolutionScale);const me=w.getRenderTarget(),he=w.getActiveCubeFace(),Ce=w.getActiveMipmapLevel();w.setRenderTarget(ne),w.getClearColor(V),k=w.getClearAlpha(),k<1&&w.setClearColor(16777215,.5),w.clear(),Xe&&we.render(H);const De=w.toneMapping;w.toneMapping=Bi;const Ee=W.viewport;if(W.viewport!==void 0&&(W.viewport=void 0),h.setupLightsView(W),ze===!0&&se.setGlobalState(w.clippingPlanes,W),wo(M,H,W),Ne.updateMultisampleRenderTarget(ne),Ne.updateRenderTargetMipmap(ne),Ue.has("WEBGL_multisampled_render_to_texture")===!1){let He=!1;for(let Qe=0,gt=F.length;Qe<gt;Qe++){const at=F[Qe],nt=at.object,Te=at.geometry,ht=at.material,$e=at.group;if(ht.side===hi&&nt.layers.test(W.layers)){const ln=ht.side;ht.side=qt,ht.needsUpdate=!0,bd(nt,H,W,Te,ht,$e),ht.side=ln,ht.needsUpdate=!0,He=!0}}He===!0&&(Ne.updateMultisampleRenderTarget(ne),Ne.updateRenderTargetMipmap(ne))}w.setRenderTarget(me,he,Ce),w.setClearColor(V,k),Ee!==void 0&&(W.viewport=Ee),w.toneMapping=De}function wo(M,F,H){const W=F.isScene===!0?F.overrideMaterial:null;for(let N=0,ne=M.length;N<ne;N++){const ue=M[N],me=ue.object,he=ue.geometry,Ce=ue.group;let De=ue.material;De.allowOverride===!0&&W!==null&&(De=W),me.layers.test(H.layers)&&bd(me,F,H,he,De,Ce)}}function bd(M,F,H,W,N,ne){M.onBeforeRender(w,F,H,W,N,ne),M.modelViewMatrix.multiplyMatrices(H.matrixWorldInverse,M.matrixWorld),M.normalMatrix.getNormalMatrix(M.modelViewMatrix),N.onBeforeRender(w,F,H,W,M,ne),N.transparent===!0&&N.side===hi&&N.forceSinglePass===!1?(N.side=qt,N.needsUpdate=!0,w.renderBufferDirect(H,F,W,N,M,ne),N.side=Hi,N.needsUpdate=!0,w.renderBufferDirect(H,F,W,N,M,ne),N.side=hi):w.renderBufferDirect(H,F,W,N,M,ne),M.onAfterRender(w,F,H,W,N,ne)}function yo(M,F,H){F.isScene!==!0&&(F=Se);const W=ve.get(M),N=h.state.lights,ne=h.state.shadowsArray,ue=N.state.version,me=Y.getParameters(M,N.state,ne,F,H),he=Y.getProgramCacheKey(me);let Ce=W.programs;W.environment=M.isMeshStandardMaterial?F.environment:null,W.fog=F.fog,W.envMap=(M.isMeshStandardMaterial?vt:Dt).get(M.envMap||W.environment),W.envMapRotation=W.environment!==null&&M.envMap===null?F.environmentRotation:M.envMapRotation,Ce===void 0&&(M.addEventListener("dispose",K),Ce=new Map,W.programs=Ce);let De=Ce.get(he);if(De!==void 0){if(W.currentProgram===De&&W.lightsStateVersion===ue)return Ed(M,me),De}else me.uniforms=Y.getUniforms(M),M.onBeforeCompile(me,w),De=Y.acquireProgram(me,he),Ce.set(he,De),W.uniforms=me.uniforms;const Ee=W.uniforms;return(!M.isShaderMaterial&&!M.isRawShaderMaterial||M.clipping===!0)&&(Ee.clippingPlanes=se.uniform),Ed(M,me),W.needsLights=xg(M),W.lightsStateVersion=ue,W.needsLights&&(Ee.ambientLightColor.value=N.state.ambient,Ee.lightProbe.value=N.state.probe,Ee.directionalLights.value=N.state.directional,Ee.directionalLightShadows.value=N.state.directionalShadow,Ee.spotLights.value=N.state.spot,Ee.spotLightShadows.value=N.state.spotShadow,Ee.rectAreaLights.value=N.state.rectArea,Ee.ltc_1.value=N.state.rectAreaLTC1,Ee.ltc_2.value=N.state.rectAreaLTC2,Ee.pointLights.value=N.state.point,Ee.pointLightShadows.value=N.state.pointShadow,Ee.hemisphereLights.value=N.state.hemi,Ee.directionalShadowMap.value=N.state.directionalShadowMap,Ee.directionalShadowMatrix.value=N.state.directionalShadowMatrix,Ee.spotShadowMap.value=N.state.spotShadowMap,Ee.spotLightMatrix.value=N.state.spotLightMatrix,Ee.spotLightMap.value=N.state.spotLightMap,Ee.pointShadowMap.value=N.state.pointShadowMap,Ee.pointShadowMatrix.value=N.state.pointShadowMatrix),W.currentProgram=De,W.uniformsList=null,De}function Sd(M){if(M.uniformsList===null){const F=M.currentProgram.getUniforms();M.uniformsList=ia.seqWithValue(F.seq,M.uniforms)}return M.uniformsList}function Ed(M,F){const H=ve.get(M);H.outputColorSpace=F.outputColorSpace,H.batching=F.batching,H.batchingColor=F.batchingColor,H.instancing=F.instancing,H.instancingColor=F.instancingColor,H.instancingMorph=F.instancingMorph,H.skinning=F.skinning,H.morphTargets=F.morphTargets,H.morphNormals=F.morphNormals,H.morphColors=F.morphColors,H.morphTargetsCount=F.morphTargetsCount,H.numClippingPlanes=F.numClippingPlanes,H.numIntersection=F.numClipIntersection,H.vertexAlphas=F.vertexAlphas,H.vertexTangents=F.vertexTangents,H.toneMapping=F.toneMapping}function _g(M,F,H,W,N){F.isScene!==!0&&(F=Se),Ne.resetTextureUnits();const ne=F.fog,ue=W.isMeshStandardMaterial?F.environment:null,me=A===null?w.outputColorSpace:A.isXRRenderTarget===!0?A.texture.colorSpace:ls,he=(W.isMeshStandardMaterial?vt:Dt).get(W.envMap||ue),Ce=W.vertexColors===!0&&!!H.attributes.color&&H.attributes.color.itemSize===4,De=!!H.attributes.tangent&&(!!W.normalMap||W.anisotropy>0),Ee=!!H.morphAttributes.position,He=!!H.morphAttributes.normal,Qe=!!H.morphAttributes.color;let gt=Bi;W.toneMapped&&(A===null||A.isXRRenderTarget===!0)&&(gt=w.toneMapping);const at=H.morphAttributes.position||H.morphAttributes.normal||H.morphAttributes.color,nt=at!==void 0?at.length:0,Te=ve.get(W),ht=h.state.lights;if(ze===!0&&(j===!0||M!==y)){const Gt=M===y&&W.id===b;se.setState(W,M,Gt)}let $e=!1;W.version===Te.__version?(Te.needsLights&&Te.lightsStateVersion!==ht.state.version||Te.outputColorSpace!==me||N.isBatchedMesh&&Te.batching===!1||!N.isBatchedMesh&&Te.batching===!0||N.isBatchedMesh&&Te.batchingColor===!0&&N.colorTexture===null||N.isBatchedMesh&&Te.batchingColor===!1&&N.colorTexture!==null||N.isInstancedMesh&&Te.instancing===!1||!N.isInstancedMesh&&Te.instancing===!0||N.isSkinnedMesh&&Te.skinning===!1||!N.isSkinnedMesh&&Te.skinning===!0||N.isInstancedMesh&&Te.instancingColor===!0&&N.instanceColor===null||N.isInstancedMesh&&Te.instancingColor===!1&&N.instanceColor!==null||N.isInstancedMesh&&Te.instancingMorph===!0&&N.morphTexture===null||N.isInstancedMesh&&Te.instancingMorph===!1&&N.morphTexture!==null||Te.envMap!==he||W.fog===!0&&Te.fog!==ne||Te.numClippingPlanes!==void 0&&(Te.numClippingPlanes!==se.numPlanes||Te.numIntersection!==se.numIntersection)||Te.vertexAlphas!==Ce||Te.vertexTangents!==De||Te.morphTargets!==Ee||Te.morphNormals!==He||Te.morphColors!==Qe||Te.toneMapping!==gt||Te.morphTargetsCount!==nt)&&($e=!0):($e=!0,Te.__version=W.version);let ln=Te.currentProgram;$e===!0&&(ln=yo(W,F,N));let Tr=!1,cn=!1,Ms=!1;const ft=ln.getUniforms(),bn=Te.uniforms;if(_e.useProgram(ln.program)&&(Tr=!0,cn=!0,Ms=!0),W.id!==b&&(b=W.id,cn=!0),Tr||y!==M){_e.buffers.depth.getReversed()&&M.reversedDepth!==!0&&(M._reversedDepth=!0,M.updateProjectionMatrix()),ft.setValue(L,"projectionMatrix",M.projectionMatrix),ft.setValue(L,"viewMatrix",M.matrixWorldInverse);const Jt=ft.map.cameraPosition;Jt!==void 0&&Jt.setValue(L,pe.setFromMatrixPosition(M.matrixWorld)),Re.logarithmicDepthBuffer&&ft.setValue(L,"logDepthBufFC",2/(Math.log(M.far+1)/Math.LN2)),(W.isMeshPhongMaterial||W.isMeshToonMaterial||W.isMeshLambertMaterial||W.isMeshBasicMaterial||W.isMeshStandardMaterial||W.isShaderMaterial)&&ft.setValue(L,"isOrthographic",M.isOrthographicCamera===!0),y!==M&&(y=M,cn=!0,Ms=!0)}if(N.isSkinnedMesh){ft.setOptional(L,N,"bindMatrix"),ft.setOptional(L,N,"bindMatrixInverse");const Gt=N.skeleton;Gt&&(Gt.boneTexture===null&&Gt.computeBoneTexture(),ft.setValue(L,"boneTexture",Gt.boneTexture,Ne))}N.isBatchedMesh&&(ft.setOptional(L,N,"batchingTexture"),ft.setValue(L,"batchingTexture",N._matricesTexture,Ne),ft.setOptional(L,N,"batchingIdTexture"),ft.setValue(L,"batchingIdTexture",N._indirectTexture,Ne),ft.setOptional(L,N,"batchingColorTexture"),N._colorsTexture!==null&&ft.setValue(L,"batchingColorTexture",N._colorsTexture,Ne));const Sn=H.morphAttributes;if((Sn.position!==void 0||Sn.normal!==void 0||Sn.color!==void 0)&&ie.update(N,H,ln),(cn||Te.receiveShadow!==N.receiveShadow)&&(Te.receiveShadow=N.receiveShadow,ft.setValue(L,"receiveShadow",N.receiveShadow)),W.isMeshGouraudMaterial&&W.envMap!==null&&(bn.envMap.value=he,bn.flipEnvMap.value=he.isCubeTexture&&he.isRenderTargetTexture===!1?-1:1),W.isMeshStandardMaterial&&W.envMap===null&&F.environment!==null&&(bn.envMapIntensity.value=F.environmentIntensity),cn&&(ft.setValue(L,"toneMappingExposure",w.toneMappingExposure),Te.needsLights&&vg(bn,Ms),ne&&W.fog===!0&&J.refreshFogUniforms(bn,ne),J.refreshMaterialUniforms(bn,W,U,$,h.state.transmissionRenderTarget[M.id]),ia.upload(L,Sd(Te),bn,Ne)),W.isShaderMaterial&&W.uniformsNeedUpdate===!0&&(ia.upload(L,Sd(Te),bn,Ne),W.uniformsNeedUpdate=!1),W.isSpriteMaterial&&ft.setValue(L,"center",N.center),ft.setValue(L,"modelViewMatrix",N.modelViewMatrix),ft.setValue(L,"normalMatrix",N.normalMatrix),ft.setValue(L,"modelMatrix",N.matrixWorld),W.isShaderMaterial||W.isRawShaderMaterial){const Gt=W.uniformsGroups;for(let Jt=0,Ya=Gt.length;Jt<Ya;Jt++){const qi=Gt[Jt];Oe.update(qi,ln),Oe.bind(qi,ln)}}return ln}function vg(M,F){M.ambientLightColor.needsUpdate=F,M.lightProbe.needsUpdate=F,M.directionalLights.needsUpdate=F,M.directionalLightShadows.needsUpdate=F,M.pointLights.needsUpdate=F,M.pointLightShadows.needsUpdate=F,M.spotLights.needsUpdate=F,M.spotLightShadows.needsUpdate=F,M.rectAreaLights.needsUpdate=F,M.hemisphereLights.needsUpdate=F}function xg(M){return M.isMeshLambertMaterial||M.isMeshToonMaterial||M.isMeshPhongMaterial||M.isMeshStandardMaterial||M.isShadowMaterial||M.isShaderMaterial&&M.lights===!0}this.getActiveCubeFace=function(){return C},this.getActiveMipmapLevel=function(){return T},this.getRenderTarget=function(){return A},this.setRenderTargetTextures=function(M,F,H){const W=ve.get(M);W.__autoAllocateDepthBuffer=M.resolveDepthBuffer===!1,W.__autoAllocateDepthBuffer===!1&&(W.__useRenderToTexture=!1),ve.get(M.texture).__webglTexture=F,ve.get(M.depthTexture).__webglTexture=W.__autoAllocateDepthBuffer?void 0:H,W.__hasExternalTextures=!0},this.setRenderTargetFramebuffer=function(M,F){const H=ve.get(M);H.__webglFramebuffer=F,H.__useDefaultFramebuffer=F===void 0};const wg=L.createFramebuffer();this.setRenderTarget=function(M,F=0,H=0){A=M,C=F,T=H;let W=!0,N=null,ne=!1,ue=!1;if(M){const he=ve.get(M);if(he.__useDefaultFramebuffer!==void 0)_e.bindFramebuffer(L.FRAMEBUFFER,null),W=!1;else if(he.__webglFramebuffer===void 0)Ne.setupRenderTarget(M);else if(he.__hasExternalTextures)Ne.rebindTextures(M,ve.get(M.texture).__webglTexture,ve.get(M.depthTexture).__webglTexture);else if(M.depthBuffer){const Ee=M.depthTexture;if(he.__boundDepthTexture!==Ee){if(Ee!==null&&ve.has(Ee)&&(M.width!==Ee.image.width||M.height!==Ee.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");Ne.setupDepthRenderbuffer(M)}}const Ce=M.texture;(Ce.isData3DTexture||Ce.isDataArrayTexture||Ce.isCompressedArrayTexture)&&(ue=!0);const De=ve.get(M).__webglFramebuffer;M.isWebGLCubeRenderTarget?(Array.isArray(De[F])?N=De[F][H]:N=De[F],ne=!0):M.samples>0&&Ne.useMultisampledRTT(M)===!1?N=ve.get(M).__webglMultisampledFramebuffer:Array.isArray(De)?N=De[H]:N=De,P.copy(M.viewport),D.copy(M.scissor),O=M.scissorTest}else P.copy(ce).multiplyScalar(U).floor(),D.copy(Ae).multiplyScalar(U).floor(),O=Je;if(H!==0&&(N=wg),_e.bindFramebuffer(L.FRAMEBUFFER,N)&&W&&_e.drawBuffers(M,N),_e.viewport(P),_e.scissor(D),_e.setScissorTest(O),ne){const he=ve.get(M.texture);L.framebufferTexture2D(L.FRAMEBUFFER,L.COLOR_ATTACHMENT0,L.TEXTURE_CUBE_MAP_POSITIVE_X+F,he.__webglTexture,H)}else if(ue){const he=F;for(let Ce=0;Ce<M.textures.length;Ce++){const De=ve.get(M.textures[Ce]);L.framebufferTextureLayer(L.FRAMEBUFFER,L.COLOR_ATTACHMENT0+Ce,De.__webglTexture,H,he)}}else if(M!==null&&H!==0){const he=ve.get(M.texture);L.framebufferTexture2D(L.FRAMEBUFFER,L.COLOR_ATTACHMENT0,L.TEXTURE_2D,he.__webglTexture,H)}b=-1},this.readRenderTargetPixels=function(M,F,H,W,N,ne,ue,me=0){if(!(M&&M.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let he=ve.get(M).__webglFramebuffer;if(M.isWebGLCubeRenderTarget&&ue!==void 0&&(he=he[ue]),he){_e.bindFramebuffer(L.FRAMEBUFFER,he);try{const Ce=M.textures[me],De=Ce.format,Ee=Ce.type;if(!Re.textureFormatReadable(De)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!Re.textureTypeReadable(Ee)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}F>=0&&F<=M.width-W&&H>=0&&H<=M.height-N&&(M.textures.length>1&&L.readBuffer(L.COLOR_ATTACHMENT0+me),L.readPixels(F,H,W,N,ye.convert(De),ye.convert(Ee),ne))}finally{const Ce=A!==null?ve.get(A).__webglFramebuffer:null;_e.bindFramebuffer(L.FRAMEBUFFER,Ce)}}},this.readRenderTargetPixelsAsync=async function(M,F,H,W,N,ne,ue,me=0){if(!(M&&M.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let he=ve.get(M).__webglFramebuffer;if(M.isWebGLCubeRenderTarget&&ue!==void 0&&(he=he[ue]),he)if(F>=0&&F<=M.width-W&&H>=0&&H<=M.height-N){_e.bindFramebuffer(L.FRAMEBUFFER,he);const Ce=M.textures[me],De=Ce.format,Ee=Ce.type;if(!Re.textureFormatReadable(De))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!Re.textureTypeReadable(Ee))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");const He=L.createBuffer();L.bindBuffer(L.PIXEL_PACK_BUFFER,He),L.bufferData(L.PIXEL_PACK_BUFFER,ne.byteLength,L.STREAM_READ),M.textures.length>1&&L.readBuffer(L.COLOR_ATTACHMENT0+me),L.readPixels(F,H,W,N,ye.convert(De),ye.convert(Ee),0);const Qe=A!==null?ve.get(A).__webglFramebuffer:null;_e.bindFramebuffer(L.FRAMEBUFFER,Qe);const gt=L.fenceSync(L.SYNC_GPU_COMMANDS_COMPLETE,0);return L.flush(),await Ny(L,gt,4),L.bindBuffer(L.PIXEL_PACK_BUFFER,He),L.getBufferSubData(L.PIXEL_PACK_BUFFER,0,ne),L.deleteBuffer(He),L.deleteSync(gt),ne}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")},this.copyFramebufferToTexture=function(M,F=null,H=0){const W=Math.pow(2,-H),N=Math.floor(M.image.width*W),ne=Math.floor(M.image.height*W),ue=F!==null?F.x:0,me=F!==null?F.y:0;Ne.setTexture2D(M,0),L.copyTexSubImage2D(L.TEXTURE_2D,H,0,0,ue,me,N,ne),_e.unbindTexture()};const yg=L.createFramebuffer(),bg=L.createFramebuffer();this.copyTextureToTexture=function(M,F,H=null,W=null,N=0,ne=null){ne===null&&(N!==0?(Js("WebGLRenderer: copyTextureToTexture function signature has changed to support src and dst mipmap levels."),ne=N,N=0):ne=0);let ue,me,he,Ce,De,Ee,He,Qe,gt;const at=M.isCompressedTexture?M.mipmaps[ne]:M.image;if(H!==null)ue=H.max.x-H.min.x,me=H.max.y-H.min.y,he=H.isBox3?H.max.z-H.min.z:1,Ce=H.min.x,De=H.min.y,Ee=H.isBox3?H.min.z:0;else{const Sn=Math.pow(2,-N);ue=Math.floor(at.width*Sn),me=Math.floor(at.height*Sn),M.isDataArrayTexture?he=at.depth:M.isData3DTexture?he=Math.floor(at.depth*Sn):he=1,Ce=0,De=0,Ee=0}W!==null?(He=W.x,Qe=W.y,gt=W.z):(He=0,Qe=0,gt=0);const nt=ye.convert(F.format),Te=ye.convert(F.type);let ht;F.isData3DTexture?(Ne.setTexture3D(F,0),ht=L.TEXTURE_3D):F.isDataArrayTexture||F.isCompressedArrayTexture?(Ne.setTexture2DArray(F,0),ht=L.TEXTURE_2D_ARRAY):(Ne.setTexture2D(F,0),ht=L.TEXTURE_2D),L.pixelStorei(L.UNPACK_FLIP_Y_WEBGL,F.flipY),L.pixelStorei(L.UNPACK_PREMULTIPLY_ALPHA_WEBGL,F.premultiplyAlpha),L.pixelStorei(L.UNPACK_ALIGNMENT,F.unpackAlignment);const $e=L.getParameter(L.UNPACK_ROW_LENGTH),ln=L.getParameter(L.UNPACK_IMAGE_HEIGHT),Tr=L.getParameter(L.UNPACK_SKIP_PIXELS),cn=L.getParameter(L.UNPACK_SKIP_ROWS),Ms=L.getParameter(L.UNPACK_SKIP_IMAGES);L.pixelStorei(L.UNPACK_ROW_LENGTH,at.width),L.pixelStorei(L.UNPACK_IMAGE_HEIGHT,at.height),L.pixelStorei(L.UNPACK_SKIP_PIXELS,Ce),L.pixelStorei(L.UNPACK_SKIP_ROWS,De),L.pixelStorei(L.UNPACK_SKIP_IMAGES,Ee);const ft=M.isDataArrayTexture||M.isData3DTexture,bn=F.isDataArrayTexture||F.isData3DTexture;if(M.isDepthTexture){const Sn=ve.get(M),Gt=ve.get(F),Jt=ve.get(Sn.__renderTarget),Ya=ve.get(Gt.__renderTarget);_e.bindFramebuffer(L.READ_FRAMEBUFFER,Jt.__webglFramebuffer),_e.bindFramebuffer(L.DRAW_FRAMEBUFFER,Ya.__webglFramebuffer);for(let qi=0;qi<he;qi++)ft&&(L.framebufferTextureLayer(L.READ_FRAMEBUFFER,L.COLOR_ATTACHMENT0,ve.get(M).__webglTexture,N,Ee+qi),L.framebufferTextureLayer(L.DRAW_FRAMEBUFFER,L.COLOR_ATTACHMENT0,ve.get(F).__webglTexture,ne,gt+qi)),L.blitFramebuffer(Ce,De,ue,me,He,Qe,ue,me,L.DEPTH_BUFFER_BIT,L.NEAREST);_e.bindFramebuffer(L.READ_FRAMEBUFFER,null),_e.bindFramebuffer(L.DRAW_FRAMEBUFFER,null)}else if(N!==0||M.isRenderTargetTexture||ve.has(M)){const Sn=ve.get(M),Gt=ve.get(F);_e.bindFramebuffer(L.READ_FRAMEBUFFER,yg),_e.bindFramebuffer(L.DRAW_FRAMEBUFFER,bg);for(let Jt=0;Jt<he;Jt++)ft?L.framebufferTextureLayer(L.READ_FRAMEBUFFER,L.COLOR_ATTACHMENT0,Sn.__webglTexture,N,Ee+Jt):L.framebufferTexture2D(L.READ_FRAMEBUFFER,L.COLOR_ATTACHMENT0,L.TEXTURE_2D,Sn.__webglTexture,N),bn?L.framebufferTextureLayer(L.DRAW_FRAMEBUFFER,L.COLOR_ATTACHMENT0,Gt.__webglTexture,ne,gt+Jt):L.framebufferTexture2D(L.DRAW_FRAMEBUFFER,L.COLOR_ATTACHMENT0,L.TEXTURE_2D,Gt.__webglTexture,ne),N!==0?L.blitFramebuffer(Ce,De,ue,me,He,Qe,ue,me,L.COLOR_BUFFER_BIT,L.NEAREST):bn?L.copyTexSubImage3D(ht,ne,He,Qe,gt+Jt,Ce,De,ue,me):L.copyTexSubImage2D(ht,ne,He,Qe,Ce,De,ue,me);_e.bindFramebuffer(L.READ_FRAMEBUFFER,null),_e.bindFramebuffer(L.DRAW_FRAMEBUFFER,null)}else bn?M.isDataTexture||M.isData3DTexture?L.texSubImage3D(ht,ne,He,Qe,gt,ue,me,he,nt,Te,at.data):F.isCompressedArrayTexture?L.compressedTexSubImage3D(ht,ne,He,Qe,gt,ue,me,he,nt,at.data):L.texSubImage3D(ht,ne,He,Qe,gt,ue,me,he,nt,Te,at):M.isDataTexture?L.texSubImage2D(L.TEXTURE_2D,ne,He,Qe,ue,me,nt,Te,at.data):M.isCompressedTexture?L.compressedTexSubImage2D(L.TEXTURE_2D,ne,He,Qe,at.width,at.height,nt,at.data):L.texSubImage2D(L.TEXTURE_2D,ne,He,Qe,ue,me,nt,Te,at);L.pixelStorei(L.UNPACK_ROW_LENGTH,$e),L.pixelStorei(L.UNPACK_IMAGE_HEIGHT,ln),L.pixelStorei(L.UNPACK_SKIP_PIXELS,Tr),L.pixelStorei(L.UNPACK_SKIP_ROWS,cn),L.pixelStorei(L.UNPACK_SKIP_IMAGES,Ms),ne===0&&F.generateMipmaps&&L.generateMipmap(ht),_e.unbindTexture()},this.initRenderTarget=function(M){ve.get(M).__webglFramebuffer===void 0&&Ne.setupRenderTarget(M)},this.initTexture=function(M){M.isCubeTexture?Ne.setTextureCube(M,0):M.isData3DTexture?Ne.setTexture3D(M,0):M.isDataArrayTexture||M.isCompressedArrayTexture?Ne.setTexture2DArray(M,0):Ne.setTexture2D(M,0),_e.unbindTexture()},this.resetState=function(){C=0,T=0,A=null,_e.reset(),le.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Yn}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorSpace=qe._getDrawingBufferColorSpace(e),t.unpackColorSpace=qe._getUnpackColorSpace()}}const Yh={type:"change"},Qu={type:"start"},gm={type:"end"},jo=new Ku,jh=new Ci,s1=Math.cos(70*Kc.DEG2RAD),At=new B,Qt=2*Math.PI,tt={NONE:-1,ROTATE:0,DOLLY:1,PAN:2,TOUCH_ROTATE:3,TOUCH_PAN:4,TOUCH_DOLLY_PAN:5,TOUCH_DOLLY_ROTATE:6},Vl=1e-6;class o1 extends yb{constructor(e,t=null){super(e,t),this.state=tt.NONE,this.target=new B,this.cursor=new B,this.minDistance=0,this.maxDistance=1/0,this.minZoom=0,this.maxZoom=1/0,this.minTargetRadius=0,this.maxTargetRadius=1/0,this.minPolarAngle=0,this.maxPolarAngle=Math.PI,this.minAzimuthAngle=-1/0,this.maxAzimuthAngle=1/0,this.enableDamping=!1,this.dampingFactor=.05,this.enableZoom=!0,this.zoomSpeed=1,this.enableRotate=!0,this.rotateSpeed=1,this.keyRotateSpeed=1,this.enablePan=!0,this.panSpeed=1,this.screenSpacePanning=!0,this.keyPanSpeed=7,this.zoomToCursor=!1,this.autoRotate=!1,this.autoRotateSpeed=2,this.keys={LEFT:"ArrowLeft",UP:"ArrowUp",RIGHT:"ArrowRight",BOTTOM:"ArrowDown"},this.mouseButtons={LEFT:Kr.ROTATE,MIDDLE:Kr.DOLLY,RIGHT:Kr.PAN},this.touches={ONE:Wr.ROTATE,TWO:Wr.DOLLY_PAN},this.target0=this.target.clone(),this.position0=this.object.position.clone(),this.zoom0=this.object.zoom,this._domElementKeyEvents=null,this._lastPosition=new B,this._lastQuaternion=new vr,this._lastTargetPosition=new B,this._quat=new vr().setFromUnitVectors(e.up,new B(0,1,0)),this._quatInverse=this._quat.clone().invert(),this._spherical=new Jc,this._sphericalDelta=new Jc,this._scale=1,this._panOffset=new B,this._rotateStart=new Be,this._rotateEnd=new Be,this._rotateDelta=new Be,this._panStart=new Be,this._panEnd=new Be,this._panDelta=new Be,this._dollyStart=new Be,this._dollyEnd=new Be,this._dollyDelta=new Be,this._dollyDirection=new B,this._mouse=new Be,this._performCursorZoom=!1,this._pointers=[],this._pointerPositions={},this._controlActive=!1,this._onPointerMove=l1.bind(this),this._onPointerDown=a1.bind(this),this._onPointerUp=c1.bind(this),this._onContextMenu=g1.bind(this),this._onMouseWheel=h1.bind(this),this._onKeyDown=f1.bind(this),this._onTouchStart=p1.bind(this),this._onTouchMove=m1.bind(this),this._onMouseDown=u1.bind(this),this._onMouseMove=d1.bind(this),this._interceptControlDown=_1.bind(this),this._interceptControlUp=v1.bind(this),this.domElement!==null&&this.connect(this.domElement),this.update()}connect(e){super.connect(e),this.domElement.addEventListener("pointerdown",this._onPointerDown),this.domElement.addEventListener("pointercancel",this._onPointerUp),this.domElement.addEventListener("contextmenu",this._onContextMenu),this.domElement.addEventListener("wheel",this._onMouseWheel,{passive:!1}),this.domElement.getRootNode().addEventListener("keydown",this._interceptControlDown,{passive:!0,capture:!0}),this.domElement.style.touchAction="none"}disconnect(){this.domElement.removeEventListener("pointerdown",this._onPointerDown),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.domElement.removeEventListener("pointercancel",this._onPointerUp),this.domElement.removeEventListener("wheel",this._onMouseWheel),this.domElement.removeEventListener("contextmenu",this._onContextMenu),this.stopListenToKeyEvents(),this.domElement.getRootNode().removeEventListener("keydown",this._interceptControlDown,{capture:!0}),this.domElement.style.touchAction="auto"}dispose(){this.disconnect()}getPolarAngle(){return this._spherical.phi}getAzimuthalAngle(){return this._spherical.theta}getDistance(){return this.object.position.distanceTo(this.target)}listenToKeyEvents(e){e.addEventListener("keydown",this._onKeyDown),this._domElementKeyEvents=e}stopListenToKeyEvents(){this._domElementKeyEvents!==null&&(this._domElementKeyEvents.removeEventListener("keydown",this._onKeyDown),this._domElementKeyEvents=null)}saveState(){this.target0.copy(this.target),this.position0.copy(this.object.position),this.zoom0=this.object.zoom}reset(){this.target.copy(this.target0),this.object.position.copy(this.position0),this.object.zoom=this.zoom0,this.object.updateProjectionMatrix(),this.dispatchEvent(Yh),this.update(),this.state=tt.NONE}update(e=null){const t=this.object.position;At.copy(t).sub(this.target),At.applyQuaternion(this._quat),this._spherical.setFromVector3(At),this.autoRotate&&this.state===tt.NONE&&this._rotateLeft(this._getAutoRotationAngle(e)),this.enableDamping?(this._spherical.theta+=this._sphericalDelta.theta*this.dampingFactor,this._spherical.phi+=this._sphericalDelta.phi*this.dampingFactor):(this._spherical.theta+=this._sphericalDelta.theta,this._spherical.phi+=this._sphericalDelta.phi);let i=this.minAzimuthAngle,r=this.maxAzimuthAngle;isFinite(i)&&isFinite(r)&&(i<-Math.PI?i+=Qt:i>Math.PI&&(i-=Qt),r<-Math.PI?r+=Qt:r>Math.PI&&(r-=Qt),i<=r?this._spherical.theta=Math.max(i,Math.min(r,this._spherical.theta)):this._spherical.theta=this._spherical.theta>(i+r)/2?Math.max(i,this._spherical.theta):Math.min(r,this._spherical.theta)),this._spherical.phi=Math.max(this.minPolarAngle,Math.min(this.maxPolarAngle,this._spherical.phi)),this._spherical.makeSafe(),this.enableDamping===!0?this.target.addScaledVector(this._panOffset,this.dampingFactor):this.target.add(this._panOffset),this.target.sub(this.cursor),this.target.clampLength(this.minTargetRadius,this.maxTargetRadius),this.target.add(this.cursor);let s=!1;if(this.zoomToCursor&&this._performCursorZoom||this.object.isOrthographicCamera)this._spherical.radius=this._clampDistance(this._spherical.radius);else{const o=this._spherical.radius;this._spherical.radius=this._clampDistance(this._spherical.radius*this._scale),s=o!=this._spherical.radius}if(At.setFromSpherical(this._spherical),At.applyQuaternion(this._quatInverse),t.copy(this.target).add(At),this.object.lookAt(this.target),this.enableDamping===!0?(this._sphericalDelta.theta*=1-this.dampingFactor,this._sphericalDelta.phi*=1-this.dampingFactor,this._panOffset.multiplyScalar(1-this.dampingFactor)):(this._sphericalDelta.set(0,0,0),this._panOffset.set(0,0,0)),this.zoomToCursor&&this._performCursorZoom){let o=null;if(this.object.isPerspectiveCamera){const a=At.length();o=this._clampDistance(a*this._scale);const l=a-o;this.object.position.addScaledVector(this._dollyDirection,l),this.object.updateMatrixWorld(),s=!!l}else if(this.object.isOrthographicCamera){const a=new B(this._mouse.x,this._mouse.y,0);a.unproject(this.object);const l=this.object.zoom;this.object.zoom=Math.max(this.minZoom,Math.min(this.maxZoom,this.object.zoom/this._scale)),this.object.updateProjectionMatrix(),s=l!==this.object.zoom;const c=new B(this._mouse.x,this._mouse.y,0);c.unproject(this.object),this.object.position.sub(c).add(a),this.object.updateMatrixWorld(),o=At.length()}else console.warn("WARNING: OrbitControls.js encountered an unknown camera type - zoom to cursor disabled."),this.zoomToCursor=!1;o!==null&&(this.screenSpacePanning?this.target.set(0,0,-1).transformDirection(this.object.matrix).multiplyScalar(o).add(this.object.position):(jo.origin.copy(this.object.position),jo.direction.set(0,0,-1).transformDirection(this.object.matrix),Math.abs(this.object.up.dot(jo.direction))<s1?this.object.lookAt(this.target):(jh.setFromNormalAndCoplanarPoint(this.object.up,this.target),jo.intersectPlane(jh,this.target))))}else if(this.object.isOrthographicCamera){const o=this.object.zoom;this.object.zoom=Math.max(this.minZoom,Math.min(this.maxZoom,this.object.zoom/this._scale)),o!==this.object.zoom&&(this.object.updateProjectionMatrix(),s=!0)}return this._scale=1,this._performCursorZoom=!1,s||this._lastPosition.distanceToSquared(this.object.position)>Vl||8*(1-this._lastQuaternion.dot(this.object.quaternion))>Vl||this._lastTargetPosition.distanceToSquared(this.target)>Vl?(this.dispatchEvent(Yh),this._lastPosition.copy(this.object.position),this._lastQuaternion.copy(this.object.quaternion),this._lastTargetPosition.copy(this.target),!0):!1}_getAutoRotationAngle(e){return e!==null?Qt/60*this.autoRotateSpeed*e:Qt/60/60*this.autoRotateSpeed}_getZoomScale(e){const t=Math.abs(e*.01);return Math.pow(.95,this.zoomSpeed*t)}_rotateLeft(e){this._sphericalDelta.theta-=e}_rotateUp(e){this._sphericalDelta.phi-=e}_panLeft(e,t){At.setFromMatrixColumn(t,0),At.multiplyScalar(-e),this._panOffset.add(At)}_panUp(e,t){this.screenSpacePanning===!0?At.setFromMatrixColumn(t,1):(At.setFromMatrixColumn(t,0),At.crossVectors(this.object.up,At)),At.multiplyScalar(e),this._panOffset.add(At)}_pan(e,t){const i=this.domElement;if(this.object.isPerspectiveCamera){const r=this.object.position;At.copy(r).sub(this.target);let s=At.length();s*=Math.tan(this.object.fov/2*Math.PI/180),this._panLeft(2*e*s/i.clientHeight,this.object.matrix),this._panUp(2*t*s/i.clientHeight,this.object.matrix)}else this.object.isOrthographicCamera?(this._panLeft(e*(this.object.right-this.object.left)/this.object.zoom/i.clientWidth,this.object.matrix),this._panUp(t*(this.object.top-this.object.bottom)/this.object.zoom/i.clientHeight,this.object.matrix)):(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - pan disabled."),this.enablePan=!1)}_dollyOut(e){this.object.isPerspectiveCamera||this.object.isOrthographicCamera?this._scale/=e:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),this.enableZoom=!1)}_dollyIn(e){this.object.isPerspectiveCamera||this.object.isOrthographicCamera?this._scale*=e:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),this.enableZoom=!1)}_updateZoomParameters(e,t){if(!this.zoomToCursor)return;this._performCursorZoom=!0;const i=this.domElement.getBoundingClientRect(),r=e-i.left,s=t-i.top,o=i.width,a=i.height;this._mouse.x=r/o*2-1,this._mouse.y=-(s/a)*2+1,this._dollyDirection.set(this._mouse.x,this._mouse.y,1).unproject(this.object).sub(this.object.position).normalize()}_clampDistance(e){return Math.max(this.minDistance,Math.min(this.maxDistance,e))}_handleMouseDownRotate(e){this._rotateStart.set(e.clientX,e.clientY)}_handleMouseDownDolly(e){this._updateZoomParameters(e.clientX,e.clientX),this._dollyStart.set(e.clientX,e.clientY)}_handleMouseDownPan(e){this._panStart.set(e.clientX,e.clientY)}_handleMouseMoveRotate(e){this._rotateEnd.set(e.clientX,e.clientY),this._rotateDelta.subVectors(this._rotateEnd,this._rotateStart).multiplyScalar(this.rotateSpeed);const t=this.domElement;this._rotateLeft(Qt*this._rotateDelta.x/t.clientHeight),this._rotateUp(Qt*this._rotateDelta.y/t.clientHeight),this._rotateStart.copy(this._rotateEnd),this.update()}_handleMouseMoveDolly(e){this._dollyEnd.set(e.clientX,e.clientY),this._dollyDelta.subVectors(this._dollyEnd,this._dollyStart),this._dollyDelta.y>0?this._dollyOut(this._getZoomScale(this._dollyDelta.y)):this._dollyDelta.y<0&&this._dollyIn(this._getZoomScale(this._dollyDelta.y)),this._dollyStart.copy(this._dollyEnd),this.update()}_handleMouseMovePan(e){this._panEnd.set(e.clientX,e.clientY),this._panDelta.subVectors(this._panEnd,this._panStart).multiplyScalar(this.panSpeed),this._pan(this._panDelta.x,this._panDelta.y),this._panStart.copy(this._panEnd),this.update()}_handleMouseWheel(e){this._updateZoomParameters(e.clientX,e.clientY),e.deltaY<0?this._dollyIn(this._getZoomScale(e.deltaY)):e.deltaY>0&&this._dollyOut(this._getZoomScale(e.deltaY)),this.update()}_handleKeyDown(e){let t=!1;switch(e.code){case this.keys.UP:e.ctrlKey||e.metaKey||e.shiftKey?this.enableRotate&&this._rotateUp(Qt*this.keyRotateSpeed/this.domElement.clientHeight):this.enablePan&&this._pan(0,this.keyPanSpeed),t=!0;break;case this.keys.BOTTOM:e.ctrlKey||e.metaKey||e.shiftKey?this.enableRotate&&this._rotateUp(-Qt*this.keyRotateSpeed/this.domElement.clientHeight):this.enablePan&&this._pan(0,-this.keyPanSpeed),t=!0;break;case this.keys.LEFT:e.ctrlKey||e.metaKey||e.shiftKey?this.enableRotate&&this._rotateLeft(Qt*this.keyRotateSpeed/this.domElement.clientHeight):this.enablePan&&this._pan(this.keyPanSpeed,0),t=!0;break;case this.keys.RIGHT:e.ctrlKey||e.metaKey||e.shiftKey?this.enableRotate&&this._rotateLeft(-Qt*this.keyRotateSpeed/this.domElement.clientHeight):this.enablePan&&this._pan(-this.keyPanSpeed,0),t=!0;break}t&&(e.preventDefault(),this.update())}_handleTouchStartRotate(e){if(this._pointers.length===1)this._rotateStart.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),i=.5*(e.pageX+t.x),r=.5*(e.pageY+t.y);this._rotateStart.set(i,r)}}_handleTouchStartPan(e){if(this._pointers.length===1)this._panStart.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),i=.5*(e.pageX+t.x),r=.5*(e.pageY+t.y);this._panStart.set(i,r)}}_handleTouchStartDolly(e){const t=this._getSecondPointerPosition(e),i=e.pageX-t.x,r=e.pageY-t.y,s=Math.sqrt(i*i+r*r);this._dollyStart.set(0,s)}_handleTouchStartDollyPan(e){this.enableZoom&&this._handleTouchStartDolly(e),this.enablePan&&this._handleTouchStartPan(e)}_handleTouchStartDollyRotate(e){this.enableZoom&&this._handleTouchStartDolly(e),this.enableRotate&&this._handleTouchStartRotate(e)}_handleTouchMoveRotate(e){if(this._pointers.length==1)this._rotateEnd.set(e.pageX,e.pageY);else{const i=this._getSecondPointerPosition(e),r=.5*(e.pageX+i.x),s=.5*(e.pageY+i.y);this._rotateEnd.set(r,s)}this._rotateDelta.subVectors(this._rotateEnd,this._rotateStart).multiplyScalar(this.rotateSpeed);const t=this.domElement;this._rotateLeft(Qt*this._rotateDelta.x/t.clientHeight),this._rotateUp(Qt*this._rotateDelta.y/t.clientHeight),this._rotateStart.copy(this._rotateEnd)}_handleTouchMovePan(e){if(this._pointers.length===1)this._panEnd.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),i=.5*(e.pageX+t.x),r=.5*(e.pageY+t.y);this._panEnd.set(i,r)}this._panDelta.subVectors(this._panEnd,this._panStart).multiplyScalar(this.panSpeed),this._pan(this._panDelta.x,this._panDelta.y),this._panStart.copy(this._panEnd)}_handleTouchMoveDolly(e){const t=this._getSecondPointerPosition(e),i=e.pageX-t.x,r=e.pageY-t.y,s=Math.sqrt(i*i+r*r);this._dollyEnd.set(0,s),this._dollyDelta.set(0,Math.pow(this._dollyEnd.y/this._dollyStart.y,this.zoomSpeed)),this._dollyOut(this._dollyDelta.y),this._dollyStart.copy(this._dollyEnd);const o=(e.pageX+t.x)*.5,a=(e.pageY+t.y)*.5;this._updateZoomParameters(o,a)}_handleTouchMoveDollyPan(e){this.enableZoom&&this._handleTouchMoveDolly(e),this.enablePan&&this._handleTouchMovePan(e)}_handleTouchMoveDollyRotate(e){this.enableZoom&&this._handleTouchMoveDolly(e),this.enableRotate&&this._handleTouchMoveRotate(e)}_addPointer(e){this._pointers.push(e.pointerId)}_removePointer(e){delete this._pointerPositions[e.pointerId];for(let t=0;t<this._pointers.length;t++)if(this._pointers[t]==e.pointerId){this._pointers.splice(t,1);return}}_isTrackingPointer(e){for(let t=0;t<this._pointers.length;t++)if(this._pointers[t]==e.pointerId)return!0;return!1}_trackPointer(e){let t=this._pointerPositions[e.pointerId];t===void 0&&(t=new Be,this._pointerPositions[e.pointerId]=t),t.set(e.pageX,e.pageY)}_getSecondPointerPosition(e){const t=e.pointerId===this._pointers[0]?this._pointers[1]:this._pointers[0];return this._pointerPositions[t]}_customWheelEvent(e){const t=e.deltaMode,i={clientX:e.clientX,clientY:e.clientY,deltaY:e.deltaY};switch(t){case 1:i.deltaY*=16;break;case 2:i.deltaY*=100;break}return e.ctrlKey&&!this._controlActive&&(i.deltaY*=10),i}}function a1(n){this.enabled!==!1&&(this._pointers.length===0&&(this.domElement.setPointerCapture(n.pointerId),this.domElement.addEventListener("pointermove",this._onPointerMove),this.domElement.addEventListener("pointerup",this._onPointerUp)),!this._isTrackingPointer(n)&&(this._addPointer(n),n.pointerType==="touch"?this._onTouchStart(n):this._onMouseDown(n)))}function l1(n){this.enabled!==!1&&(n.pointerType==="touch"?this._onTouchMove(n):this._onMouseMove(n))}function c1(n){switch(this._removePointer(n),this._pointers.length){case 0:this.domElement.releasePointerCapture(n.pointerId),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.dispatchEvent(gm),this.state=tt.NONE;break;case 1:const e=this._pointers[0],t=this._pointerPositions[e];this._onTouchStart({pointerId:e,pageX:t.x,pageY:t.y});break}}function u1(n){let e;switch(n.button){case 0:e=this.mouseButtons.LEFT;break;case 1:e=this.mouseButtons.MIDDLE;break;case 2:e=this.mouseButtons.RIGHT;break;default:e=-1}switch(e){case Kr.DOLLY:if(this.enableZoom===!1)return;this._handleMouseDownDolly(n),this.state=tt.DOLLY;break;case Kr.ROTATE:if(n.ctrlKey||n.metaKey||n.shiftKey){if(this.enablePan===!1)return;this._handleMouseDownPan(n),this.state=tt.PAN}else{if(this.enableRotate===!1)return;this._handleMouseDownRotate(n),this.state=tt.ROTATE}break;case Kr.PAN:if(n.ctrlKey||n.metaKey||n.shiftKey){if(this.enableRotate===!1)return;this._handleMouseDownRotate(n),this.state=tt.ROTATE}else{if(this.enablePan===!1)return;this._handleMouseDownPan(n),this.state=tt.PAN}break;default:this.state=tt.NONE}this.state!==tt.NONE&&this.dispatchEvent(Qu)}function d1(n){switch(this.state){case tt.ROTATE:if(this.enableRotate===!1)return;this._handleMouseMoveRotate(n);break;case tt.DOLLY:if(this.enableZoom===!1)return;this._handleMouseMoveDolly(n);break;case tt.PAN:if(this.enablePan===!1)return;this._handleMouseMovePan(n);break}}function h1(n){this.enabled===!1||this.enableZoom===!1||this.state!==tt.NONE||(n.preventDefault(),this.dispatchEvent(Qu),this._handleMouseWheel(this._customWheelEvent(n)),this.dispatchEvent(gm))}function f1(n){this.enabled!==!1&&this._handleKeyDown(n)}function p1(n){switch(this._trackPointer(n),this._pointers.length){case 1:switch(this.touches.ONE){case Wr.ROTATE:if(this.enableRotate===!1)return;this._handleTouchStartRotate(n),this.state=tt.TOUCH_ROTATE;break;case Wr.PAN:if(this.enablePan===!1)return;this._handleTouchStartPan(n),this.state=tt.TOUCH_PAN;break;default:this.state=tt.NONE}break;case 2:switch(this.touches.TWO){case Wr.DOLLY_PAN:if(this.enableZoom===!1&&this.enablePan===!1)return;this._handleTouchStartDollyPan(n),this.state=tt.TOUCH_DOLLY_PAN;break;case Wr.DOLLY_ROTATE:if(this.enableZoom===!1&&this.enableRotate===!1)return;this._handleTouchStartDollyRotate(n),this.state=tt.TOUCH_DOLLY_ROTATE;break;default:this.state=tt.NONE}break;default:this.state=tt.NONE}this.state!==tt.NONE&&this.dispatchEvent(Qu)}function m1(n){switch(this._trackPointer(n),this.state){case tt.TOUCH_ROTATE:if(this.enableRotate===!1)return;this._handleTouchMoveRotate(n),this.update();break;case tt.TOUCH_PAN:if(this.enablePan===!1)return;this._handleTouchMovePan(n),this.update();break;case tt.TOUCH_DOLLY_PAN:if(this.enableZoom===!1&&this.enablePan===!1)return;this._handleTouchMoveDollyPan(n),this.update();break;case tt.TOUCH_DOLLY_ROTATE:if(this.enableZoom===!1&&this.enableRotate===!1)return;this._handleTouchMoveDollyRotate(n),this.update();break;default:this.state=tt.NONE}}function g1(n){this.enabled!==!1&&n.preventDefault()}function _1(n){n.key==="Control"&&(this._controlActive=!0,this.domElement.getRootNode().addEventListener("keyup",this._interceptControlUp,{passive:!0,capture:!0}))}function v1(n){n.key==="Control"&&(this._controlActive=!1,this.domElement.getRootNode().removeEventListener("keyup",this._interceptControlUp,{passive:!0,capture:!0}))}/**
 * lil-gui
 * https://lil-gui.georgealways.com
 * @version 0.21.0
 * @author George Michael Brower
 * @license MIT
 */class Qn{constructor(e,t,i,r,s="div"){this.parent=e,this.object=t,this.property=i,this._disabled=!1,this._hidden=!1,this.initialValue=this.getValue(),this.domElement=document.createElement(s),this.domElement.classList.add("lil-controller"),this.domElement.classList.add(r),this.$name=document.createElement("div"),this.$name.classList.add("lil-name"),Qn.nextNameID=Qn.nextNameID||0,this.$name.id=`lil-gui-name-${++Qn.nextNameID}`,this.$widget=document.createElement("div"),this.$widget.classList.add("lil-widget"),this.$disable=this.$widget,this.domElement.appendChild(this.$name),this.domElement.appendChild(this.$widget),this.domElement.addEventListener("keydown",o=>o.stopPropagation()),this.domElement.addEventListener("keyup",o=>o.stopPropagation()),this.parent.children.push(this),this.parent.controllers.push(this),this.parent.$children.appendChild(this.domElement),this._listenCallback=this._listenCallback.bind(this),this.name(i)}name(e){return this._name=e,this.$name.textContent=e,this}onChange(e){return this._onChange=e,this}_callOnChange(){this.parent._callOnChange(this),this._onChange!==void 0&&this._onChange.call(this,this.getValue()),this._changed=!0}onFinishChange(e){return this._onFinishChange=e,this}_callOnFinishChange(){this._changed&&(this.parent._callOnFinishChange(this),this._onFinishChange!==void 0&&this._onFinishChange.call(this,this.getValue())),this._changed=!1}reset(){return this.setValue(this.initialValue),this._callOnFinishChange(),this}enable(e=!0){return this.disable(!e)}disable(e=!0){return e===this._disabled?this:(this._disabled=e,this.domElement.classList.toggle("lil-disabled",e),this.$disable.toggleAttribute("disabled",e),this)}show(e=!0){return this._hidden=!e,this.domElement.style.display=this._hidden?"none":"",this}hide(){return this.show(!1)}options(e){const t=this.parent.add(this.object,this.property,e);return t.name(this._name),this.destroy(),t}min(e){return this}max(e){return this}step(e){return this}decimals(e){return this}listen(e=!0){return this._listening=e,this._listenCallbackID!==void 0&&(cancelAnimationFrame(this._listenCallbackID),this._listenCallbackID=void 0),this._listening&&this._listenCallback(),this}_listenCallback(){this._listenCallbackID=requestAnimationFrame(this._listenCallback);const e=this.save();e!==this._listenPrevValue&&this.updateDisplay(),this._listenPrevValue=e}getValue(){return this.object[this.property]}setValue(e){return this.getValue()!==e&&(this.object[this.property]=e,this._callOnChange(),this.updateDisplay()),this}updateDisplay(){return this}load(e){return this.setValue(e),this._callOnFinishChange(),this}save(){return this.getValue()}destroy(){this.listen(!1),this.parent.children.splice(this.parent.children.indexOf(this),1),this.parent.controllers.splice(this.parent.controllers.indexOf(this),1),this.parent.$children.removeChild(this.domElement)}}class x1 extends Qn{constructor(e,t,i){super(e,t,i,"lil-boolean","label"),this.$input=document.createElement("input"),this.$input.setAttribute("type","checkbox"),this.$input.setAttribute("aria-labelledby",this.$name.id),this.$widget.appendChild(this.$input),this.$input.addEventListener("change",()=>{this.setValue(this.$input.checked),this._callOnFinishChange()}),this.$disable=this.$input,this.updateDisplay()}updateDisplay(){return this.$input.checked=this.getValue(),this}}function eu(n){let e,t;return(e=n.match(/(#|0x)?([a-f0-9]{6})/i))?t=e[2]:(e=n.match(/rgb\(\s*(\d*)\s*,\s*(\d*)\s*,\s*(\d*)\s*\)/))?t=parseInt(e[1]).toString(16).padStart(2,0)+parseInt(e[2]).toString(16).padStart(2,0)+parseInt(e[3]).toString(16).padStart(2,0):(e=n.match(/^#?([a-f0-9])([a-f0-9])([a-f0-9])$/i))&&(t=e[1]+e[1]+e[2]+e[2]+e[3]+e[3]),t?"#"+t:!1}const w1={isPrimitive:!0,match:n=>typeof n=="string",fromHexString:eu,toHexString:eu},Qs={isPrimitive:!0,match:n=>typeof n=="number",fromHexString:n=>parseInt(n.substring(1),16),toHexString:n=>"#"+n.toString(16).padStart(6,0)},y1={isPrimitive:!1,match:n=>Array.isArray(n)||ArrayBuffer.isView(n),fromHexString(n,e,t=1){const i=Qs.fromHexString(n);e[0]=(i>>16&255)/255*t,e[1]=(i>>8&255)/255*t,e[2]=(i&255)/255*t},toHexString([n,e,t],i=1){i=255/i;const r=n*i<<16^e*i<<8^t*i<<0;return Qs.toHexString(r)}},b1={isPrimitive:!1,match:n=>Object(n)===n,fromHexString(n,e,t=1){const i=Qs.fromHexString(n);e.r=(i>>16&255)/255*t,e.g=(i>>8&255)/255*t,e.b=(i&255)/255*t},toHexString({r:n,g:e,b:t},i=1){i=255/i;const r=n*i<<16^e*i<<8^t*i<<0;return Qs.toHexString(r)}},S1=[w1,Qs,y1,b1];function E1(n){return S1.find(e=>e.match(n))}class M1 extends Qn{constructor(e,t,i,r){super(e,t,i,"lil-color"),this.$input=document.createElement("input"),this.$input.setAttribute("type","color"),this.$input.setAttribute("tabindex",-1),this.$input.setAttribute("aria-labelledby",this.$name.id),this.$text=document.createElement("input"),this.$text.setAttribute("type","text"),this.$text.setAttribute("spellcheck","false"),this.$text.setAttribute("aria-labelledby",this.$name.id),this.$display=document.createElement("div"),this.$display.classList.add("lil-display"),this.$display.appendChild(this.$input),this.$widget.appendChild(this.$display),this.$widget.appendChild(this.$text),this._format=E1(this.initialValue),this._rgbScale=r,this._initialValueHexString=this.save(),this._textFocused=!1,this.$input.addEventListener("input",()=>{this._setValueFromHexString(this.$input.value)}),this.$input.addEventListener("blur",()=>{this._callOnFinishChange()}),this.$text.addEventListener("input",()=>{const s=eu(this.$text.value);s&&this._setValueFromHexString(s)}),this.$text.addEventListener("focus",()=>{this._textFocused=!0,this.$text.select()}),this.$text.addEventListener("blur",()=>{this._textFocused=!1,this.updateDisplay(),this._callOnFinishChange()}),this.$disable=this.$text,this.updateDisplay()}reset(){return this._setValueFromHexString(this._initialValueHexString),this}_setValueFromHexString(e){if(this._format.isPrimitive){const t=this._format.fromHexString(e);this.setValue(t)}else this._format.fromHexString(e,this.getValue(),this._rgbScale),this._callOnChange(),this.updateDisplay()}save(){return this._format.toHexString(this.getValue(),this._rgbScale)}load(e){return this._setValueFromHexString(e),this._callOnFinishChange(),this}updateDisplay(){return this.$input.value=this._format.toHexString(this.getValue(),this._rgbScale),this._textFocused||(this.$text.value=this.$input.value.substring(1)),this.$display.style.backgroundColor=this.$input.value,this}}class Hl extends Qn{constructor(e,t,i){super(e,t,i,"lil-function"),this.$button=document.createElement("button"),this.$button.appendChild(this.$name),this.$widget.appendChild(this.$button),this.$button.addEventListener("click",r=>{r.preventDefault(),this.getValue().call(this.object),this._callOnChange()}),this.$button.addEventListener("touchstart",()=>{},{passive:!0}),this.$disable=this.$button}}class T1 extends Qn{constructor(e,t,i,r,s,o){super(e,t,i,"lil-number"),this._initInput(),this.min(r),this.max(s);const a=o!==void 0;this.step(a?o:this._getImplicitStep(),a),this.updateDisplay()}decimals(e){return this._decimals=e,this.updateDisplay(),this}min(e){return this._min=e,this._onUpdateMinMax(),this}max(e){return this._max=e,this._onUpdateMinMax(),this}step(e,t=!0){return this._step=e,this._stepExplicit=t,this}updateDisplay(){const e=this.getValue();if(this._hasSlider){let t=(e-this._min)/(this._max-this._min);t=Math.max(0,Math.min(t,1)),this.$fill.style.width=t*100+"%"}return this._inputFocused||(this.$input.value=this._decimals===void 0?e:e.toFixed(this._decimals)),this}_initInput(){this.$input=document.createElement("input"),this.$input.setAttribute("type","text"),this.$input.setAttribute("aria-labelledby",this.$name.id),window.matchMedia("(pointer: coarse)").matches&&(this.$input.setAttribute("type","number"),this.$input.setAttribute("step","any")),this.$widget.appendChild(this.$input),this.$disable=this.$input;const t=()=>{let v=parseFloat(this.$input.value);isNaN(v)||(this._stepExplicit&&(v=this._snap(v)),this.setValue(this._clamp(v)))},i=v=>{const x=parseFloat(this.$input.value);isNaN(x)||(this._snapClampSetValue(x+v),this.$input.value=this.getValue())},r=v=>{v.key==="Enter"&&this.$input.blur(),v.code==="ArrowUp"&&(v.preventDefault(),i(this._step*this._arrowKeyMultiplier(v))),v.code==="ArrowDown"&&(v.preventDefault(),i(this._step*this._arrowKeyMultiplier(v)*-1))},s=v=>{this._inputFocused&&(v.preventDefault(),i(this._step*this._normalizeMouseWheel(v)))};let o=!1,a,l,c,u,d;const p=5,f=v=>{a=v.clientX,l=c=v.clientY,o=!0,u=this.getValue(),d=0,window.addEventListener("mousemove",_),window.addEventListener("mouseup",g)},_=v=>{if(o){const x=v.clientX-a,w=v.clientY-l;Math.abs(w)>p?(v.preventDefault(),this.$input.blur(),o=!1,this._setDraggingStyle(!0,"vertical")):Math.abs(x)>p&&g()}if(!o){const x=v.clientY-c;d-=x*this._step*this._arrowKeyMultiplier(v),u+d>this._max?d=this._max-u:u+d<this._min&&(d=this._min-u),this._snapClampSetValue(u+d)}c=v.clientY},g=()=>{this._setDraggingStyle(!1,"vertical"),this._callOnFinishChange(),window.removeEventListener("mousemove",_),window.removeEventListener("mouseup",g)},m=()=>{this._inputFocused=!0},h=()=>{this._inputFocused=!1,this.updateDisplay(),this._callOnFinishChange()};this.$input.addEventListener("input",t),this.$input.addEventListener("keydown",r),this.$input.addEventListener("wheel",s,{passive:!1}),this.$input.addEventListener("mousedown",f),this.$input.addEventListener("focus",m),this.$input.addEventListener("blur",h)}_initSlider(){this._hasSlider=!0,this.$slider=document.createElement("div"),this.$slider.classList.add("lil-slider"),this.$fill=document.createElement("div"),this.$fill.classList.add("lil-fill"),this.$slider.appendChild(this.$fill),this.$widget.insertBefore(this.$slider,this.$input),this.domElement.classList.add("lil-has-slider");const e=(h,v,x,w,S)=>(h-v)/(x-v)*(S-w)+w,t=h=>{const v=this.$slider.getBoundingClientRect();let x=e(h,v.left,v.right,this._min,this._max);this._snapClampSetValue(x)},i=h=>{this._setDraggingStyle(!0),t(h.clientX),window.addEventListener("mousemove",r),window.addEventListener("mouseup",s)},r=h=>{t(h.clientX)},s=()=>{this._callOnFinishChange(),this._setDraggingStyle(!1),window.removeEventListener("mousemove",r),window.removeEventListener("mouseup",s)};let o=!1,a,l;const c=h=>{h.preventDefault(),this._setDraggingStyle(!0),t(h.touches[0].clientX),o=!1},u=h=>{h.touches.length>1||(this._hasScrollBar?(a=h.touches[0].clientX,l=h.touches[0].clientY,o=!0):c(h),window.addEventListener("touchmove",d,{passive:!1}),window.addEventListener("touchend",p))},d=h=>{if(o){const v=h.touches[0].clientX-a,x=h.touches[0].clientY-l;Math.abs(v)>Math.abs(x)?c(h):(window.removeEventListener("touchmove",d),window.removeEventListener("touchend",p))}else h.preventDefault(),t(h.touches[0].clientX)},p=()=>{this._callOnFinishChange(),this._setDraggingStyle(!1),window.removeEventListener("touchmove",d),window.removeEventListener("touchend",p)},f=this._callOnFinishChange.bind(this),_=400;let g;const m=h=>{if(Math.abs(h.deltaX)<Math.abs(h.deltaY)&&this._hasScrollBar)return;h.preventDefault();const x=this._normalizeMouseWheel(h)*this._step;this._snapClampSetValue(this.getValue()+x),this.$input.value=this.getValue(),clearTimeout(g),g=setTimeout(f,_)};this.$slider.addEventListener("mousedown",i),this.$slider.addEventListener("touchstart",u,{passive:!1}),this.$slider.addEventListener("wheel",m,{passive:!1})}_setDraggingStyle(e,t="horizontal"){this.$slider&&this.$slider.classList.toggle("lil-active",e),document.body.classList.toggle("lil-dragging",e),document.body.classList.toggle(`lil-${t}`,e)}_getImplicitStep(){return this._hasMin&&this._hasMax?(this._max-this._min)/1e3:.1}_onUpdateMinMax(){!this._hasSlider&&this._hasMin&&this._hasMax&&(this._stepExplicit||this.step(this._getImplicitStep(),!1),this._initSlider(),this.updateDisplay())}_normalizeMouseWheel(e){let{deltaX:t,deltaY:i}=e;return Math.floor(e.deltaY)!==e.deltaY&&e.wheelDelta&&(t=0,i=-e.wheelDelta/120,i*=this._stepExplicit?1:10),t+-i}_arrowKeyMultiplier(e){let t=this._stepExplicit?1:10;return e.shiftKey?t*=10:e.altKey&&(t/=10),t}_snap(e){let t=0;return this._hasMin?t=this._min:this._hasMax&&(t=this._max),e-=t,e=Math.round(e/this._step)*this._step,e+=t,e=parseFloat(e.toPrecision(15)),e}_clamp(e){return e<this._min&&(e=this._min),e>this._max&&(e=this._max),e}_snapClampSetValue(e){this.setValue(this._clamp(this._snap(e)))}get _hasScrollBar(){const e=this.parent.root.$children;return e.scrollHeight>e.clientHeight}get _hasMin(){return this._min!==void 0}get _hasMax(){return this._max!==void 0}}class A1 extends Qn{constructor(e,t,i,r){super(e,t,i,"lil-option"),this.$select=document.createElement("select"),this.$select.setAttribute("aria-labelledby",this.$name.id),this.$display=document.createElement("div"),this.$display.classList.add("lil-display"),this.$select.addEventListener("change",()=>{this.setValue(this._values[this.$select.selectedIndex]),this._callOnFinishChange()}),this.$select.addEventListener("focus",()=>{this.$display.classList.add("lil-focus")}),this.$select.addEventListener("blur",()=>{this.$display.classList.remove("lil-focus")}),this.$widget.appendChild(this.$select),this.$widget.appendChild(this.$display),this.$disable=this.$select,this.options(r)}options(e){return this._values=Array.isArray(e)?e:Object.values(e),this._names=Array.isArray(e)?e:Object.keys(e),this.$select.replaceChildren(),this._names.forEach(t=>{const i=document.createElement("option");i.textContent=t,this.$select.appendChild(i)}),this.updateDisplay(),this}updateDisplay(){const e=this.getValue(),t=this._values.indexOf(e);return this.$select.selectedIndex=t,this.$display.textContent=t===-1?e:this._names[t],this}}class C1 extends Qn{constructor(e,t,i){super(e,t,i,"lil-string"),this.$input=document.createElement("input"),this.$input.setAttribute("type","text"),this.$input.setAttribute("spellcheck","false"),this.$input.setAttribute("aria-labelledby",this.$name.id),this.$input.addEventListener("input",()=>{this.setValue(this.$input.value)}),this.$input.addEventListener("keydown",r=>{r.code==="Enter"&&this.$input.blur()}),this.$input.addEventListener("blur",()=>{this._callOnFinishChange()}),this.$widget.appendChild(this.$input),this.$disable=this.$input,this.updateDisplay()}updateDisplay(){return this.$input.value=this.getValue(),this}}var P1=`.lil-gui {
  font-family: var(--font-family);
  font-size: var(--font-size);
  line-height: 1;
  font-weight: normal;
  font-style: normal;
  text-align: left;
  color: var(--text-color);
  user-select: none;
  -webkit-user-select: none;
  touch-action: manipulation;
  --background-color: #1f1f1f;
  --text-color: #ebebeb;
  --title-background-color: #111111;
  --title-text-color: #ebebeb;
  --widget-color: #424242;
  --hover-color: #4f4f4f;
  --focus-color: #595959;
  --number-color: #2cc9ff;
  --string-color: #a2db3c;
  --font-size: 11px;
  --input-font-size: 11px;
  --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
  --font-family-mono: Menlo, Monaco, Consolas, "Droid Sans Mono", monospace;
  --padding: 4px;
  --spacing: 4px;
  --widget-height: 20px;
  --title-height: calc(var(--widget-height) + var(--spacing) * 1.25);
  --name-width: 45%;
  --slider-knob-width: 2px;
  --slider-input-width: 27%;
  --color-input-width: 27%;
  --slider-input-min-width: 45px;
  --color-input-min-width: 45px;
  --folder-indent: 7px;
  --widget-padding: 0 0 0 3px;
  --widget-border-radius: 2px;
  --checkbox-size: calc(0.75 * var(--widget-height));
  --scrollbar-width: 5px;
}
.lil-gui, .lil-gui * {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
.lil-gui.lil-root {
  width: var(--width, 245px);
  display: flex;
  flex-direction: column;
  background: var(--background-color);
}
.lil-gui.lil-root > .lil-title {
  background: var(--title-background-color);
  color: var(--title-text-color);
}
.lil-gui.lil-root > .lil-children {
  overflow-x: hidden;
  overflow-y: auto;
}
.lil-gui.lil-root > .lil-children::-webkit-scrollbar {
  width: var(--scrollbar-width);
  height: var(--scrollbar-width);
  background: var(--background-color);
}
.lil-gui.lil-root > .lil-children::-webkit-scrollbar-thumb {
  border-radius: var(--scrollbar-width);
  background: var(--focus-color);
}
@media (pointer: coarse) {
  .lil-gui.lil-allow-touch-styles, .lil-gui.lil-allow-touch-styles .lil-gui {
    --widget-height: 28px;
    --padding: 6px;
    --spacing: 6px;
    --font-size: 13px;
    --input-font-size: 16px;
    --folder-indent: 10px;
    --scrollbar-width: 7px;
    --slider-input-min-width: 50px;
    --color-input-min-width: 65px;
  }
}
.lil-gui.lil-force-touch-styles, .lil-gui.lil-force-touch-styles .lil-gui {
  --widget-height: 28px;
  --padding: 6px;
  --spacing: 6px;
  --font-size: 13px;
  --input-font-size: 16px;
  --folder-indent: 10px;
  --scrollbar-width: 7px;
  --slider-input-min-width: 50px;
  --color-input-min-width: 65px;
}
.lil-gui.lil-auto-place, .lil-gui.autoPlace {
  max-height: 100%;
  position: fixed;
  top: 0;
  right: 15px;
  z-index: 1001;
}

.lil-controller {
  display: flex;
  align-items: center;
  padding: 0 var(--padding);
  margin: var(--spacing) 0;
}
.lil-controller.lil-disabled {
  opacity: 0.5;
}
.lil-controller.lil-disabled, .lil-controller.lil-disabled * {
  pointer-events: none !important;
}
.lil-controller > .lil-name {
  min-width: var(--name-width);
  flex-shrink: 0;
  white-space: pre;
  padding-right: var(--spacing);
  line-height: var(--widget-height);
}
.lil-controller .lil-widget {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  min-height: var(--widget-height);
}
.lil-controller.lil-string input {
  color: var(--string-color);
}
.lil-controller.lil-boolean {
  cursor: pointer;
}
.lil-controller.lil-color .lil-display {
  width: 100%;
  height: var(--widget-height);
  border-radius: var(--widget-border-radius);
  position: relative;
}
@media (hover: hover) {
  .lil-controller.lil-color .lil-display:hover:before {
    content: " ";
    display: block;
    position: absolute;
    border-radius: var(--widget-border-radius);
    border: 1px solid #fff9;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
  }
}
.lil-controller.lil-color input[type=color] {
  opacity: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
}
.lil-controller.lil-color input[type=text] {
  margin-left: var(--spacing);
  font-family: var(--font-family-mono);
  min-width: var(--color-input-min-width);
  width: var(--color-input-width);
  flex-shrink: 0;
}
.lil-controller.lil-option select {
  opacity: 0;
  position: absolute;
  width: 100%;
  max-width: 100%;
}
.lil-controller.lil-option .lil-display {
  position: relative;
  pointer-events: none;
  border-radius: var(--widget-border-radius);
  height: var(--widget-height);
  line-height: var(--widget-height);
  max-width: 100%;
  overflow: hidden;
  word-break: break-all;
  padding-left: 0.55em;
  padding-right: 1.75em;
  background: var(--widget-color);
}
@media (hover: hover) {
  .lil-controller.lil-option .lil-display.lil-focus {
    background: var(--focus-color);
  }
}
.lil-controller.lil-option .lil-display.lil-active {
  background: var(--focus-color);
}
.lil-controller.lil-option .lil-display:after {
  font-family: "lil-gui";
  content: "↕";
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  padding-right: 0.375em;
}
.lil-controller.lil-option .lil-widget,
.lil-controller.lil-option select {
  cursor: pointer;
}
@media (hover: hover) {
  .lil-controller.lil-option .lil-widget:hover .lil-display {
    background: var(--hover-color);
  }
}
.lil-controller.lil-number input {
  color: var(--number-color);
}
.lil-controller.lil-number.lil-has-slider input {
  margin-left: var(--spacing);
  width: var(--slider-input-width);
  min-width: var(--slider-input-min-width);
  flex-shrink: 0;
}
.lil-controller.lil-number .lil-slider {
  width: 100%;
  height: var(--widget-height);
  background: var(--widget-color);
  border-radius: var(--widget-border-radius);
  padding-right: var(--slider-knob-width);
  overflow: hidden;
  cursor: ew-resize;
  touch-action: pan-y;
}
@media (hover: hover) {
  .lil-controller.lil-number .lil-slider:hover {
    background: var(--hover-color);
  }
}
.lil-controller.lil-number .lil-slider.lil-active {
  background: var(--focus-color);
}
.lil-controller.lil-number .lil-slider.lil-active .lil-fill {
  opacity: 0.95;
}
.lil-controller.lil-number .lil-fill {
  height: 100%;
  border-right: var(--slider-knob-width) solid var(--number-color);
  box-sizing: content-box;
}

.lil-dragging .lil-gui {
  --hover-color: var(--widget-color);
}
.lil-dragging * {
  cursor: ew-resize !important;
}
.lil-dragging.lil-vertical * {
  cursor: ns-resize !important;
}

.lil-gui .lil-title {
  height: var(--title-height);
  font-weight: 600;
  padding: 0 var(--padding);
  width: 100%;
  text-align: left;
  background: none;
  text-decoration-skip: objects;
}
.lil-gui .lil-title:before {
  font-family: "lil-gui";
  content: "▾";
  padding-right: 2px;
  display: inline-block;
}
.lil-gui .lil-title:active {
  background: var(--title-background-color);
  opacity: 0.75;
}
@media (hover: hover) {
  body:not(.lil-dragging) .lil-gui .lil-title:hover {
    background: var(--title-background-color);
    opacity: 0.85;
  }
  .lil-gui .lil-title:focus {
    text-decoration: underline var(--focus-color);
  }
}
.lil-gui.lil-root > .lil-title:focus {
  text-decoration: none !important;
}
.lil-gui.lil-closed > .lil-title:before {
  content: "▸";
}
.lil-gui.lil-closed > .lil-children {
  transform: translateY(-7px);
  opacity: 0;
}
.lil-gui.lil-closed:not(.lil-transition) > .lil-children {
  display: none;
}
.lil-gui.lil-transition > .lil-children {
  transition-duration: 300ms;
  transition-property: height, opacity, transform;
  transition-timing-function: cubic-bezier(0.2, 0.6, 0.35, 1);
  overflow: hidden;
  pointer-events: none;
}
.lil-gui .lil-children:empty:before {
  content: "Empty";
  padding: 0 var(--padding);
  margin: var(--spacing) 0;
  display: block;
  height: var(--widget-height);
  font-style: italic;
  line-height: var(--widget-height);
  opacity: 0.5;
}
.lil-gui.lil-root > .lil-children > .lil-gui > .lil-title {
  border: 0 solid var(--widget-color);
  border-width: 1px 0;
  transition: border-color 300ms;
}
.lil-gui.lil-root > .lil-children > .lil-gui.lil-closed > .lil-title {
  border-bottom-color: transparent;
}
.lil-gui + .lil-controller {
  border-top: 1px solid var(--widget-color);
  margin-top: 0;
  padding-top: var(--spacing);
}
.lil-gui .lil-gui .lil-gui > .lil-title {
  border: none;
}
.lil-gui .lil-gui .lil-gui > .lil-children {
  border: none;
  margin-left: var(--folder-indent);
  border-left: 2px solid var(--widget-color);
}
.lil-gui .lil-gui .lil-controller {
  border: none;
}

.lil-gui label, .lil-gui input, .lil-gui button {
  -webkit-tap-highlight-color: transparent;
}
.lil-gui input {
  border: 0;
  outline: none;
  font-family: var(--font-family);
  font-size: var(--input-font-size);
  border-radius: var(--widget-border-radius);
  height: var(--widget-height);
  background: var(--widget-color);
  color: var(--text-color);
  width: 100%;
}
@media (hover: hover) {
  .lil-gui input:hover {
    background: var(--hover-color);
  }
  .lil-gui input:active {
    background: var(--focus-color);
  }
}
.lil-gui input:disabled {
  opacity: 1;
}
.lil-gui input[type=text],
.lil-gui input[type=number] {
  padding: var(--widget-padding);
  -moz-appearance: textfield;
}
.lil-gui input[type=text]:focus,
.lil-gui input[type=number]:focus {
  background: var(--focus-color);
}
.lil-gui input[type=checkbox] {
  appearance: none;
  width: var(--checkbox-size);
  height: var(--checkbox-size);
  border-radius: var(--widget-border-radius);
  text-align: center;
  cursor: pointer;
}
.lil-gui input[type=checkbox]:checked:before {
  font-family: "lil-gui";
  content: "✓";
  font-size: var(--checkbox-size);
  line-height: var(--checkbox-size);
}
@media (hover: hover) {
  .lil-gui input[type=checkbox]:focus {
    box-shadow: inset 0 0 0 1px var(--focus-color);
  }
}
.lil-gui button {
  outline: none;
  cursor: pointer;
  font-family: var(--font-family);
  font-size: var(--font-size);
  color: var(--text-color);
  width: 100%;
  border: none;
}
.lil-gui .lil-controller button {
  height: var(--widget-height);
  text-transform: none;
  background: var(--widget-color);
  border-radius: var(--widget-border-radius);
}
@media (hover: hover) {
  .lil-gui .lil-controller button:hover {
    background: var(--hover-color);
  }
  .lil-gui .lil-controller button:focus {
    box-shadow: inset 0 0 0 1px var(--focus-color);
  }
}
.lil-gui .lil-controller button:active {
  background: var(--focus-color);
}

@font-face {
  font-family: "lil-gui";
  src: url("data:application/font-woff2;charset=utf-8;base64,d09GMgABAAAAAALkAAsAAAAABtQAAAKVAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHFQGYACDMgqBBIEbATYCJAMUCwwABCAFhAoHgQQbHAbIDiUFEYVARAAAYQTVWNmz9MxhEgodq49wYRUFKE8GWNiUBxI2LBRaVnc51U83Gmhs0Q7JXWMiz5eteLwrKwuxHO8VFxUX9UpZBs6pa5ABRwHA+t3UxUnH20EvVknRerzQgX6xC/GH6ZUvTcAjAv122dF28OTqCXrPuyaDER30YBA1xnkVutDDo4oCi71Ca7rrV9xS8dZHbPHefsuwIyCpmT7j+MnjAH5X3984UZoFFuJ0yiZ4XEJFxjagEBeqs+e1iyK8Xf/nOuwF+vVK0ur765+vf7txotUi0m3N0m/84RGSrBCNrh8Ee5GjODjF4gnWP+dJrH/Lk9k4oT6d+gr6g/wssA2j64JJGP6cmx554vUZnpZfn6ZfX2bMwPPrlANsB86/DiHjhl0OP+c87+gaJo/gY084s3HoYL/ZkWHTRfBXvvoHnnkHvngKun4KBE/ede7tvq3/vQOxDXB1/fdNz6XbPdcr0Vhpojj9dG+owuSKFsslCi1tgEjirjXdwMiov2EioadxmqTHUCIwo8NgQaeIasAi0fTYSPTbSmwbMOFduyh9wvBrESGY0MtgRjtgQR8Q1bRPohn2UoCRZf9wyYANMXFeJTysqAe0I4mrherOekFdKMrYvJjLvOIUM9SuwYB5DVZUwwVjJJOaUnZCmcEkIZZrKqNvRGRMvmFZsmhP4VMKCSXBhSqUBxgMS7h0cZvEd71AWkEhGWaeMFcNnpqyJkyXgYL7PQ1MoSq0wDAkRtJIijkZSmqYTiSImfLiSWXIZwhRh3Rug2X0kk1Dgj+Iu43u5p98ghopcpSo0Uyc8SnjlYX59WUeaMoDqmVD2TOWD9a4pCRAzf2ECgwGcrHjPOWY9bNxq/OL3I/QjwEAAAA=") format("woff2");
}`;function R1(n){const e=document.createElement("style");e.innerHTML=n;const t=document.querySelector("head link[rel=stylesheet], head style");t?document.head.insertBefore(e,t):document.head.appendChild(e)}let Kh=!1;class ed{constructor({parent:e,autoPlace:t=e===void 0,container:i,width:r,title:s="Controls",closeFolders:o=!1,injectStyles:a=!0,touchStyles:l=!0}={}){if(this.parent=e,this.root=e?e.root:this,this.children=[],this.controllers=[],this.folders=[],this._closed=!1,this._hidden=!1,this.domElement=document.createElement("div"),this.domElement.classList.add("lil-gui"),this.$title=document.createElement("button"),this.$title.classList.add("lil-title"),this.$title.setAttribute("aria-expanded",!0),this.$title.addEventListener("click",()=>this.openAnimated(this._closed)),this.$title.addEventListener("touchstart",()=>{},{passive:!0}),this.$children=document.createElement("div"),this.$children.classList.add("lil-children"),this.domElement.appendChild(this.$title),this.domElement.appendChild(this.$children),this.title(s),this.parent){this.parent.children.push(this),this.parent.folders.push(this),this.parent.$children.appendChild(this.domElement);return}this.domElement.classList.add("lil-root"),l&&this.domElement.classList.add("lil-allow-touch-styles"),!Kh&&a&&(R1(P1),Kh=!0),i?i.appendChild(this.domElement):t&&(this.domElement.classList.add("lil-auto-place","autoPlace"),document.body.appendChild(this.domElement)),r&&this.domElement.style.setProperty("--width",r+"px"),this._closeFolders=o}add(e,t,i,r,s){if(Object(i)===i)return new A1(this,e,t,i);const o=e[t];switch(typeof o){case"number":return new T1(this,e,t,i,r,s);case"boolean":return new x1(this,e,t);case"string":return new C1(this,e,t);case"function":return new Hl(this,e,t)}console.error(`gui.add failed
	property:`,t,`
	object:`,e,`
	value:`,o)}addColor(e,t,i=1){return new M1(this,e,t,i)}addFolder(e){const t=new ed({parent:this,title:e});return this.root._closeFolders&&t.close(),t}load(e,t=!0){return e.controllers&&this.controllers.forEach(i=>{i instanceof Hl||i._name in e.controllers&&i.load(e.controllers[i._name])}),t&&e.folders&&this.folders.forEach(i=>{i._title in e.folders&&i.load(e.folders[i._title])}),this}save(e=!0){const t={controllers:{},folders:{}};return this.controllers.forEach(i=>{if(!(i instanceof Hl)){if(i._name in t.controllers)throw new Error(`Cannot save GUI with duplicate property "${i._name}"`);t.controllers[i._name]=i.save()}}),e&&this.folders.forEach(i=>{if(i._title in t.folders)throw new Error(`Cannot save GUI with duplicate folder "${i._title}"`);t.folders[i._title]=i.save()}),t}open(e=!0){return this._setClosed(!e),this.$title.setAttribute("aria-expanded",!this._closed),this.domElement.classList.toggle("lil-closed",this._closed),this}close(){return this.open(!1)}_setClosed(e){this._closed!==e&&(this._closed=e,this._callOnOpenClose(this))}show(e=!0){return this._hidden=!e,this.domElement.style.display=this._hidden?"none":"",this}hide(){return this.show(!1)}openAnimated(e=!0){return this._setClosed(!e),this.$title.setAttribute("aria-expanded",!this._closed),requestAnimationFrame(()=>{const t=this.$children.clientHeight;this.$children.style.height=t+"px",this.domElement.classList.add("lil-transition");const i=s=>{s.target===this.$children&&(this.$children.style.height="",this.domElement.classList.remove("lil-transition"),this.$children.removeEventListener("transitionend",i))};this.$children.addEventListener("transitionend",i);const r=e?this.$children.scrollHeight:0;this.domElement.classList.toggle("lil-closed",!e),requestAnimationFrame(()=>{this.$children.style.height=r+"px"})}),this}title(e){return this._title=e,this.$title.textContent=e,this}reset(e=!0){return(e?this.controllersRecursive():this.controllers).forEach(i=>i.reset()),this}onChange(e){return this._onChange=e,this}_callOnChange(e){this.parent&&this.parent._callOnChange(e),this._onChange!==void 0&&this._onChange.call(this,{object:e.object,property:e.property,value:e.getValue(),controller:e})}onFinishChange(e){return this._onFinishChange=e,this}_callOnFinishChange(e){this.parent&&this.parent._callOnFinishChange(e),this._onFinishChange!==void 0&&this._onFinishChange.call(this,{object:e.object,property:e.property,value:e.getValue(),controller:e})}onOpenClose(e){return this._onOpenClose=e,this}_callOnOpenClose(e){this.parent&&this.parent._callOnOpenClose(e),this._onOpenClose!==void 0&&this._onOpenClose.call(this,e)}destroy(){this.parent&&(this.parent.children.splice(this.parent.children.indexOf(this),1),this.parent.folders.splice(this.parent.folders.indexOf(this),1)),this.domElement.parentElement&&this.domElement.parentElement.removeChild(this.domElement),Array.from(this.children).forEach(e=>e.destroy())}controllersRecursive(){let e=Array.from(this.controllers);return this.folders.forEach(t=>{e=e.concat(t.controllersRecursive())}),e}foldersRecursive(){let e=Array.from(this.folders);return this.folders.forEach(t=>{e=e.concat(t.foldersRecursive())}),e}}var D1=`uniform float uSize;
uniform vec2 uResolution;
uniform float uProgress;

attribute float aSize;
attribute float aTimeMultiplier;

float remap(float value, float originMin, float originMax, float destinationMin, float destinationMax)
{
    return destinationMin + (value - originMin) * (destinationMax - destinationMin) / (originMax - originMin);
}

void main()
{
    float progress = uProgress;
    progress *= aTimeMultiplier;

    
    vec3 newPosition = position;

    
    float explodingProgress = remap(progress, 0.0, 0.1, 0.0, 1.0);
    explodingProgress = clamp(explodingProgress, 0.0, 1.0);
    explodingProgress = 1.0 - pow(1.0 - explodingProgress, 3.0); 
    newPosition *= explodingProgress;

    
    float fallingProgress = remap(progress, 0.1, 1.0, 0.0, 1.0);
    fallingProgress = clamp(fallingProgress, 0.0, 1.0);
    fallingProgress = 1.0 - pow(1.0 - fallingProgress, 3.0);
    newPosition.y -= fallingProgress * 0.2;

    
    float sizeOpeningProgress = remap(progress, 0.0, 0.125, 0.0, 1.0);
    float sizeClosingProgress = remap(progress, 0.125, 1.0, 1.0, 0.0);
    float sizeProgress = min(sizeOpeningProgress, sizeClosingProgress);
    sizeProgress = clamp(sizeProgress, 0.0, 1.0);

    
    float twinklingProgress = remap(progress, 0.2, 0.8, 0.0, 1.0);
    twinklingProgress = clamp(twinklingProgress, 0.0, 1.0);
    float sizeTwinkling = sin(progress * 30.0) * 0.5 + 0.5;
    sizeTwinkling = 1.0 - sizeTwinkling * twinklingProgress;

    
    vec4 modelPosition = modelMatrix * vec4(newPosition, 1.0);
    vec4 viewPosition = viewMatrix * modelPosition;
    gl_Position = projectionMatrix * viewPosition;

    
    gl_PointSize = uSize * uResolution.y * aSize * sizeProgress * sizeTwinkling;
    gl_PointSize *= 1.0 / - viewPosition.z;
    if(gl_PointSize < 1.0) 
        gl_Position = vec4(9999.9);
}`,L1=`uniform sampler2D uTexture;
uniform vec3 uColor;

void main()
{
    float textureAlpha = texture(uTexture, gl_PointCoord).r;
    

    
    gl_FragColor = vec4(uColor, textureAlpha);
    
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
}`;function ui(n){if(n===void 0)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return n}function _m(n,e){n.prototype=Object.create(e.prototype),n.prototype.constructor=n,n.__proto__=e}/*!
 * GSAP 3.13.0
 * https://gsap.com
 *
 * @license Copyright 2008-2025, GreenSock. All rights reserved.
 * Subject to the terms at https://gsap.com/standard-license
 * @author: Jack Doyle, jack@greensock.com
*/var gn={autoSleep:120,force3D:"auto",nullTargetWarn:1,units:{lineHeight:""}},us={duration:.5,overwrite:!1,delay:0},td,Ft,dt,Pn=1e8,rt=1/Pn,tu=Math.PI*2,I1=tu/4,U1=0,vm=Math.sqrt,O1=Math.cos,F1=Math.sin,Ot=function(e){return typeof e=="string"},_t=function(e){return typeof e=="function"},xi=function(e){return typeof e=="number"},nd=function(e){return typeof e>"u"},ni=function(e){return typeof e=="object"},nn=function(e){return e!==!1},id=function(){return typeof window<"u"},Ko=function(e){return _t(e)||Ot(e)},xm=typeof ArrayBuffer=="function"&&ArrayBuffer.isView||function(){},Vt=Array.isArray,nu=/(?:-?\.?\d|\.)+/gi,wm=/[-+=.]*\d+[.e\-+]*\d*[e\-+]*\d*/g,$r=/[-+=.]*\d+[.e-]*\d*[a-z%]*/g,Gl=/[-+=.]*\d+\.?\d*(?:e-|e\+)?\d*/gi,ym=/[+-]=-?[.\d]+/,bm=/[^,'"\[\]\s]+/gi,N1=/^[+\-=e\s\d]*\d+[.\d]*([a-z]*|%)\s*$/i,pt,Hn,iu,rd,vn={},Ea={},Sm,Em=function(e){return(Ea=ds(e,vn))&&an},sd=function(e,t){return console.warn("Invalid property",e,"set to",t,"Missing plugin? gsap.registerPlugin()")},eo=function(e,t){return!t&&console.warn(e)},Mm=function(e,t){return e&&(vn[e]=t)&&Ea&&(Ea[e]=t)||vn},to=function(){return 0},k1={suppressEvents:!0,isStart:!0,kill:!1},ra={suppressEvents:!0,kill:!1},B1={suppressEvents:!0},od={},zi=[],ru={},Tm,fn={},Wl={},Zh=30,sa=[],ad="",ld=function(e){var t=e[0],i,r;if(ni(t)||_t(t)||(e=[e]),!(i=(t._gsap||{}).harness)){for(r=sa.length;r--&&!sa[r].targetTest(t););i=sa[r]}for(r=e.length;r--;)e[r]&&(e[r]._gsap||(e[r]._gsap=new Km(e[r],i)))||e.splice(r,1);return e},hr=function(e){return e._gsap||ld(Rn(e))[0]._gsap},Am=function(e,t,i){return(i=e[t])&&_t(i)?e[t]():nd(i)&&e.getAttribute&&e.getAttribute(t)||i},rn=function(e,t){return(e=e.split(",")).forEach(t)||e},wt=function(e){return Math.round(e*1e5)/1e5||0},Mt=function(e){return Math.round(e*1e7)/1e7||0},Qr=function(e,t){var i=t.charAt(0),r=parseFloat(t.substr(2));return e=parseFloat(e),i==="+"?e+r:i==="-"?e-r:i==="*"?e*r:e/r},z1=function(e,t){for(var i=t.length,r=0;e.indexOf(t[r])<0&&++r<i;);return r<i},Ma=function(){var e=zi.length,t=zi.slice(0),i,r;for(ru={},zi.length=0,i=0;i<e;i++)r=t[i],r&&r._lazy&&(r.render(r._lazy[0],r._lazy[1],!0)._lazy=0)},cd=function(e){return!!(e._initted||e._startAt||e.add)},Cm=function(e,t,i,r){zi.length&&!Ft&&Ma(),e.render(t,i,!!(Ft&&t<0&&cd(e))),zi.length&&!Ft&&Ma()},Pm=function(e){var t=parseFloat(e);return(t||t===0)&&(e+"").match(bm).length<2?t:Ot(e)?e.trim():e},Rm=function(e){return e},xn=function(e,t){for(var i in t)i in e||(e[i]=t[i]);return e},V1=function(e){return function(t,i){for(var r in i)r in t||r==="duration"&&e||r==="ease"||(t[r]=i[r])}},ds=function(e,t){for(var i in t)e[i]=t[i];return e},Jh=function n(e,t){for(var i in t)i!=="__proto__"&&i!=="constructor"&&i!=="prototype"&&(e[i]=ni(t[i])?n(e[i]||(e[i]={}),t[i]):t[i]);return e},Ta=function(e,t){var i={},r;for(r in e)r in t||(i[r]=e[r]);return i},zs=function(e){var t=e.parent||pt,i=e.keyframes?V1(Vt(e.keyframes)):xn;if(nn(e.inherit))for(;t;)i(e,t.vars.defaults),t=t.parent||t._dp;return e},H1=function(e,t){for(var i=e.length,r=i===t.length;r&&i--&&e[i]===t[i];);return i<0},Dm=function(e,t,i,r,s){var o=e[r],a;if(s)for(a=t[s];o&&o[s]>a;)o=o._prev;return o?(t._next=o._next,o._next=t):(t._next=e[i],e[i]=t),t._next?t._next._prev=t:e[r]=t,t._prev=o,t.parent=t._dp=e,t},Ga=function(e,t,i,r){i===void 0&&(i="_first"),r===void 0&&(r="_last");var s=t._prev,o=t._next;s?s._next=o:e[i]===t&&(e[i]=o),o?o._prev=s:e[r]===t&&(e[r]=s),t._next=t._prev=t.parent=null},Gi=function(e,t){e.parent&&(!t||e.parent.autoRemoveChildren)&&e.parent.remove&&e.parent.remove(e),e._act=0},fr=function(e,t){if(e&&(!t||t._end>e._dur||t._start<0))for(var i=e;i;)i._dirty=1,i=i.parent;return e},G1=function(e){for(var t=e.parent;t&&t.parent;)t._dirty=1,t.totalDuration(),t=t.parent;return e},su=function(e,t,i,r){return e._startAt&&(Ft?e._startAt.revert(ra):e.vars.immediateRender&&!e.vars.autoRevert||e._startAt.render(t,!0,r))},W1=function n(e){return!e||e._ts&&n(e.parent)},Qh=function(e){return e._repeat?hs(e._tTime,e=e.duration()+e._rDelay)*e:0},hs=function(e,t){var i=Math.floor(e=Mt(e/t));return e&&i===e?i-1:i},Aa=function(e,t){return(e-t._start)*t._ts+(t._ts>=0?0:t._dirty?t.totalDuration():t._tDur)},Wa=function(e){return e._end=Mt(e._start+(e._tDur/Math.abs(e._ts||e._rts||rt)||0))},Xa=function(e,t){var i=e._dp;return i&&i.smoothChildTiming&&e._ts&&(e._start=Mt(i._time-(e._ts>0?t/e._ts:((e._dirty?e.totalDuration():e._tDur)-t)/-e._ts)),Wa(e),i._dirty||fr(i,e)),e},Lm=function(e,t){var i;if((t._time||!t._dur&&t._initted||t._start<e._time&&(t._dur||!t.add))&&(i=Aa(e.rawTime(),t),(!t._dur||xo(0,t.totalDuration(),i)-t._tTime>rt)&&t.render(i,!0)),fr(e,t)._dp&&e._initted&&e._time>=e._dur&&e._ts){if(e._dur<e.duration())for(i=e;i._dp;)i.rawTime()>=0&&i.totalTime(i._tTime),i=i._dp;e._zTime=-rt}},Xn=function(e,t,i,r){return t.parent&&Gi(t),t._start=Mt((xi(i)?i:i||e!==pt?Mn(e,i,t):e._time)+t._delay),t._end=Mt(t._start+(t.totalDuration()/Math.abs(t.timeScale())||0)),Dm(e,t,"_first","_last",e._sort?"_start":0),ou(t)||(e._recent=t),r||Lm(e,t),e._ts<0&&Xa(e,e._tTime),e},Im=function(e,t){return(vn.ScrollTrigger||sd("scrollTrigger",t))&&vn.ScrollTrigger.create(t,e)},Um=function(e,t,i,r,s){if(dd(e,t,s),!e._initted)return 1;if(!i&&e._pt&&!Ft&&(e._dur&&e.vars.lazy!==!1||!e._dur&&e.vars.lazy)&&Tm!==pn.frame)return zi.push(e),e._lazy=[s,r],1},X1=function n(e){var t=e.parent;return t&&t._ts&&t._initted&&!t._lock&&(t.rawTime()<0||n(t))},ou=function(e){var t=e.data;return t==="isFromStart"||t==="isStart"},$1=function(e,t,i,r){var s=e.ratio,o=t<0||!t&&(!e._start&&X1(e)&&!(!e._initted&&ou(e))||(e._ts<0||e._dp._ts<0)&&!ou(e))?0:1,a=e._rDelay,l=0,c,u,d;if(a&&e._repeat&&(l=xo(0,e._tDur,t),u=hs(l,a),e._yoyo&&u&1&&(o=1-o),u!==hs(e._tTime,a)&&(s=1-o,e.vars.repeatRefresh&&e._initted&&e.invalidate())),o!==s||Ft||r||e._zTime===rt||!t&&e._zTime){if(!e._initted&&Um(e,t,r,i,l))return;for(d=e._zTime,e._zTime=t||(i?rt:0),i||(i=t&&!d),e.ratio=o,e._from&&(o=1-o),e._time=0,e._tTime=l,c=e._pt;c;)c.r(o,c.d),c=c._next;t<0&&su(e,t,i,!0),e._onUpdate&&!i&&mn(e,"onUpdate"),l&&e._repeat&&!i&&e.parent&&mn(e,"onRepeat"),(t>=e._tDur||t<0)&&e.ratio===o&&(o&&Gi(e,1),!i&&!Ft&&(mn(e,o?"onComplete":"onReverseComplete",!0),e._prom&&e._prom()))}else e._zTime||(e._zTime=t)},q1=function(e,t,i){var r;if(i>t)for(r=e._first;r&&r._start<=i;){if(r.data==="isPause"&&r._start>t)return r;r=r._next}else for(r=e._last;r&&r._start>=i;){if(r.data==="isPause"&&r._start<t)return r;r=r._prev}},fs=function(e,t,i,r){var s=e._repeat,o=Mt(t)||0,a=e._tTime/e._tDur;return a&&!r&&(e._time*=o/e._dur),e._dur=o,e._tDur=s?s<0?1e10:Mt(o*(s+1)+e._rDelay*s):o,a>0&&!r&&Xa(e,e._tTime=e._tDur*a),e.parent&&Wa(e),i||fr(e.parent,e),e},ef=function(e){return e instanceof $t?fr(e):fs(e,e._dur)},Y1={_start:0,endTime:to,totalDuration:to},Mn=function n(e,t,i){var r=e.labels,s=e._recent||Y1,o=e.duration()>=Pn?s.endTime(!1):e._dur,a,l,c;return Ot(t)&&(isNaN(t)||t in r)?(l=t.charAt(0),c=t.substr(-1)==="%",a=t.indexOf("="),l==="<"||l===">"?(a>=0&&(t=t.replace(/=/,"")),(l==="<"?s._start:s.endTime(s._repeat>=0))+(parseFloat(t.substr(1))||0)*(c?(a<0?s:i).totalDuration()/100:1)):a<0?(t in r||(r[t]=o),r[t]):(l=parseFloat(t.charAt(a-1)+t.substr(a+1)),c&&i&&(l=l/100*(Vt(i)?i[0]:i).totalDuration()),a>1?n(e,t.substr(0,a-1),i)+l:o+l)):t==null?o:+t},Vs=function(e,t,i){var r=xi(t[1]),s=(r?2:1)+(e<2?0:1),o=t[s],a,l;if(r&&(o.duration=t[1]),o.parent=i,e){for(a=o,l=i;l&&!("immediateRender"in a);)a=l.vars.defaults||{},l=nn(l.vars.inherit)&&l.parent;o.immediateRender=nn(a.immediateRender),e<2?o.runBackwards=1:o.startAt=t[s-1]}return new Et(t[0],o,t[s+1])},Xi=function(e,t){return e||e===0?t(e):t},xo=function(e,t,i){return i<e?e:i>t?t:i},zt=function(e,t){return!Ot(e)||!(t=N1.exec(e))?"":t[1]},j1=function(e,t,i){return Xi(i,function(r){return xo(e,t,r)})},au=[].slice,Om=function(e,t){return e&&ni(e)&&"length"in e&&(!t&&!e.length||e.length-1 in e&&ni(e[0]))&&!e.nodeType&&e!==Hn},K1=function(e,t,i){return i===void 0&&(i=[]),e.forEach(function(r){var s;return Ot(r)&&!t||Om(r,1)?(s=i).push.apply(s,Rn(r)):i.push(r)})||i},Rn=function(e,t,i){return dt&&!t&&dt.selector?dt.selector(e):Ot(e)&&!i&&(iu||!ps())?au.call((t||rd).querySelectorAll(e),0):Vt(e)?K1(e,i):Om(e)?au.call(e,0):e?[e]:[]},lu=function(e){return e=Rn(e)[0]||eo("Invalid scope")||{},function(t){var i=e.current||e.nativeElement||e;return Rn(t,i.querySelectorAll?i:i===e?eo("Invalid scope")||rd.createElement("div"):e)}},Fm=function(e){return e.sort(function(){return .5-Math.random()})},Nm=function(e){if(_t(e))return e;var t=ni(e)?e:{each:e},i=pr(t.ease),r=t.from||0,s=parseFloat(t.base)||0,o={},a=r>0&&r<1,l=isNaN(r)||a,c=t.axis,u=r,d=r;return Ot(r)?u=d={center:.5,edges:.5,end:1}[r]||0:!a&&l&&(u=r[0],d=r[1]),function(p,f,_){var g=(_||t).length,m=o[g],h,v,x,w,S,C,T,A,b;if(!m){if(b=t.grid==="auto"?0:(t.grid||[1,Pn])[1],!b){for(T=-Pn;T<(T=_[b++].getBoundingClientRect().left)&&b<g;);b<g&&b--}for(m=o[g]=[],h=l?Math.min(b,g)*u-.5:r%b,v=b===Pn?0:l?g*d/b-.5:r/b|0,T=0,A=Pn,C=0;C<g;C++)x=C%b-h,w=v-(C/b|0),m[C]=S=c?Math.abs(c==="y"?w:x):vm(x*x+w*w),S>T&&(T=S),S<A&&(A=S);r==="random"&&Fm(m),m.max=T-A,m.min=A,m.v=g=(parseFloat(t.amount)||parseFloat(t.each)*(b>g?g-1:c?c==="y"?g/b:b:Math.max(b,g/b))||0)*(r==="edges"?-1:1),m.b=g<0?s-g:s,m.u=zt(t.amount||t.each)||0,i=i&&g<0?qm(i):i}return g=(m[p]-m.min)/m.max||0,Mt(m.b+(i?i(g):g)*m.v)+m.u}},cu=function(e){var t=Math.pow(10,((e+"").split(".")[1]||"").length);return function(i){var r=Mt(Math.round(parseFloat(i)/e)*e*t);return(r-r%1)/t+(xi(i)?0:zt(i))}},km=function(e,t){var i=Vt(e),r,s;return!i&&ni(e)&&(r=i=e.radius||Pn,e.values?(e=Rn(e.values),(s=!xi(e[0]))&&(r*=r)):e=cu(e.increment)),Xi(t,i?_t(e)?function(o){return s=e(o),Math.abs(s-o)<=r?s:o}:function(o){for(var a=parseFloat(s?o.x:o),l=parseFloat(s?o.y:0),c=Pn,u=0,d=e.length,p,f;d--;)s?(p=e[d].x-a,f=e[d].y-l,p=p*p+f*f):p=Math.abs(e[d]-a),p<c&&(c=p,u=d);return u=!r||c<=r?e[u]:o,s||u===o||xi(o)?u:u+zt(o)}:cu(e))},Bm=function(e,t,i,r){return Xi(Vt(e)?!t:i===!0?!!(i=0):!r,function(){return Vt(e)?e[~~(Math.random()*e.length)]:(i=i||1e-5)&&(r=i<1?Math.pow(10,(i+"").length-2):1)&&Math.floor(Math.round((e-i/2+Math.random()*(t-e+i*.99))/i)*i*r)/r})},Z1=function(){for(var e=arguments.length,t=new Array(e),i=0;i<e;i++)t[i]=arguments[i];return function(r){return t.reduce(function(s,o){return o(s)},r)}},J1=function(e,t){return function(i){return e(parseFloat(i))+(t||zt(i))}},Q1=function(e,t,i){return Vm(e,t,0,1,i)},zm=function(e,t,i){return Xi(i,function(r){return e[~~t(r)]})},eA=function n(e,t,i){var r=t-e;return Vt(e)?zm(e,n(0,e.length),t):Xi(i,function(s){return(r+(s-e)%r)%r+e})},tA=function n(e,t,i){var r=t-e,s=r*2;return Vt(e)?zm(e,n(0,e.length-1),t):Xi(i,function(o){return o=(s+(o-e)%s)%s||0,e+(o>r?s-o:o)})},no=function(e){for(var t=0,i="",r,s,o,a;~(r=e.indexOf("random(",t));)o=e.indexOf(")",r),a=e.charAt(r+7)==="[",s=e.substr(r+7,o-r-7).match(a?bm:nu),i+=e.substr(t,r-t)+Bm(a?s:+s[0],a?0:+s[1],+s[2]||1e-5),t=o+1;return i+e.substr(t,e.length-t)},Vm=function(e,t,i,r,s){var o=t-e,a=r-i;return Xi(s,function(l){return i+((l-e)/o*a||0)})},nA=function n(e,t,i,r){var s=isNaN(e+t)?0:function(f){return(1-f)*e+f*t};if(!s){var o=Ot(e),a={},l,c,u,d,p;if(i===!0&&(r=1)&&(i=null),o)e={p:e},t={p:t};else if(Vt(e)&&!Vt(t)){for(u=[],d=e.length,p=d-2,c=1;c<d;c++)u.push(n(e[c-1],e[c]));d--,s=function(_){_*=d;var g=Math.min(p,~~_);return u[g](_-g)},i=t}else r||(e=ds(Vt(e)?[]:{},e));if(!u){for(l in t)ud.call(a,e,l,"get",t[l]);s=function(_){return pd(_,a)||(o?e.p:e)}}}return Xi(i,s)},tf=function(e,t,i){var r=e.labels,s=Pn,o,a,l;for(o in r)a=r[o]-t,a<0==!!i&&a&&s>(a=Math.abs(a))&&(l=o,s=a);return l},mn=function(e,t,i){var r=e.vars,s=r[t],o=dt,a=e._ctx,l,c,u;if(s)return l=r[t+"Params"],c=r.callbackScope||e,i&&zi.length&&Ma(),a&&(dt=a),u=l?s.apply(c,l):s.call(c),dt=o,u},Is=function(e){return Gi(e),e.scrollTrigger&&e.scrollTrigger.kill(!!Ft),e.progress()<1&&mn(e,"onInterrupt"),e},qr,Hm=[],Gm=function(e){if(e)if(e=!e.name&&e.default||e,id()||e.headless){var t=e.name,i=_t(e),r=t&&!i&&e.init?function(){this._props=[]}:e,s={init:to,render:pd,add:ud,kill:vA,modifier:_A,rawVars:0},o={targetTest:0,get:0,getSetter:fd,aliases:{},register:0};if(ps(),e!==r){if(fn[t])return;xn(r,xn(Ta(e,s),o)),ds(r.prototype,ds(s,Ta(e,o))),fn[r.prop=t]=r,e.targetTest&&(sa.push(r),od[t]=1),t=(t==="css"?"CSS":t.charAt(0).toUpperCase()+t.substr(1))+"Plugin"}Mm(t,r),e.register&&e.register(an,r,sn)}else Hm.push(e)},it=255,Us={aqua:[0,it,it],lime:[0,it,0],silver:[192,192,192],black:[0,0,0],maroon:[128,0,0],teal:[0,128,128],blue:[0,0,it],navy:[0,0,128],white:[it,it,it],olive:[128,128,0],yellow:[it,it,0],orange:[it,165,0],gray:[128,128,128],purple:[128,0,128],green:[0,128,0],red:[it,0,0],pink:[it,192,203],cyan:[0,it,it],transparent:[it,it,it,0]},Xl=function(e,t,i){return e+=e<0?1:e>1?-1:0,(e*6<1?t+(i-t)*e*6:e<.5?i:e*3<2?t+(i-t)*(2/3-e)*6:t)*it+.5|0},Wm=function(e,t,i){var r=e?xi(e)?[e>>16,e>>8&it,e&it]:0:Us.black,s,o,a,l,c,u,d,p,f,_;if(!r){if(e.substr(-1)===","&&(e=e.substr(0,e.length-1)),Us[e])r=Us[e];else if(e.charAt(0)==="#"){if(e.length<6&&(s=e.charAt(1),o=e.charAt(2),a=e.charAt(3),e="#"+s+s+o+o+a+a+(e.length===5?e.charAt(4)+e.charAt(4):"")),e.length===9)return r=parseInt(e.substr(1,6),16),[r>>16,r>>8&it,r&it,parseInt(e.substr(7),16)/255];e=parseInt(e.substr(1),16),r=[e>>16,e>>8&it,e&it]}else if(e.substr(0,3)==="hsl"){if(r=_=e.match(nu),!t)l=+r[0]%360/360,c=+r[1]/100,u=+r[2]/100,o=u<=.5?u*(c+1):u+c-u*c,s=u*2-o,r.length>3&&(r[3]*=1),r[0]=Xl(l+1/3,s,o),r[1]=Xl(l,s,o),r[2]=Xl(l-1/3,s,o);else if(~e.indexOf("="))return r=e.match(wm),i&&r.length<4&&(r[3]=1),r}else r=e.match(nu)||Us.transparent;r=r.map(Number)}return t&&!_&&(s=r[0]/it,o=r[1]/it,a=r[2]/it,d=Math.max(s,o,a),p=Math.min(s,o,a),u=(d+p)/2,d===p?l=c=0:(f=d-p,c=u>.5?f/(2-d-p):f/(d+p),l=d===s?(o-a)/f+(o<a?6:0):d===o?(a-s)/f+2:(s-o)/f+4,l*=60),r[0]=~~(l+.5),r[1]=~~(c*100+.5),r[2]=~~(u*100+.5)),i&&r.length<4&&(r[3]=1),r},Xm=function(e){var t=[],i=[],r=-1;return e.split(Vi).forEach(function(s){var o=s.match($r)||[];t.push.apply(t,o),i.push(r+=o.length+1)}),t.c=i,t},nf=function(e,t,i){var r="",s=(e+r).match(Vi),o=t?"hsla(":"rgba(",a=0,l,c,u,d;if(!s)return e;if(s=s.map(function(p){return(p=Wm(p,t,1))&&o+(t?p[0]+","+p[1]+"%,"+p[2]+"%,"+p[3]:p.join(","))+")"}),i&&(u=Xm(e),l=i.c,l.join(r)!==u.c.join(r)))for(c=e.replace(Vi,"1").split($r),d=c.length-1;a<d;a++)r+=c[a]+(~l.indexOf(a)?s.shift()||o+"0,0,0,0)":(u.length?u:s.length?s:i).shift());if(!c)for(c=e.split(Vi),d=c.length-1;a<d;a++)r+=c[a]+s[a];return r+c[d]},Vi=(function(){var n="(?:\\b(?:(?:rgb|rgba|hsl|hsla)\\(.+?\\))|\\B#(?:[0-9a-f]{3,4}){1,2}\\b",e;for(e in Us)n+="|"+e+"\\b";return new RegExp(n+")","gi")})(),iA=/hsl[a]?\(/,$m=function(e){var t=e.join(" "),i;if(Vi.lastIndex=0,Vi.test(t))return i=iA.test(t),e[1]=nf(e[1],i),e[0]=nf(e[0],i,Xm(e[1])),!0},io,pn=(function(){var n=Date.now,e=500,t=33,i=n(),r=i,s=1e3/240,o=s,a=[],l,c,u,d,p,f,_=function g(m){var h=n()-r,v=m===!0,x,w,S,C;if((h>e||h<0)&&(i+=h-t),r+=h,S=r-i,x=S-o,(x>0||v)&&(C=++d.frame,p=S-d.time*1e3,d.time=S=S/1e3,o+=x+(x>=s?4:s-x),w=1),v||(l=c(g)),w)for(f=0;f<a.length;f++)a[f](S,p,C,m)};return d={time:0,frame:0,tick:function(){_(!0)},deltaRatio:function(m){return p/(1e3/(m||60))},wake:function(){Sm&&(!iu&&id()&&(Hn=iu=window,rd=Hn.document||{},vn.gsap=an,(Hn.gsapVersions||(Hn.gsapVersions=[])).push(an.version),Em(Ea||Hn.GreenSockGlobals||!Hn.gsap&&Hn||{}),Hm.forEach(Gm)),u=typeof requestAnimationFrame<"u"&&requestAnimationFrame,l&&d.sleep(),c=u||function(m){return setTimeout(m,o-d.time*1e3+1|0)},io=1,_(2))},sleep:function(){(u?cancelAnimationFrame:clearTimeout)(l),io=0,c=to},lagSmoothing:function(m,h){e=m||1/0,t=Math.min(h||33,e)},fps:function(m){s=1e3/(m||240),o=d.time*1e3+s},add:function(m,h,v){var x=h?function(w,S,C,T){m(w,S,C,T),d.remove(x)}:m;return d.remove(m),a[v?"unshift":"push"](x),ps(),x},remove:function(m,h){~(h=a.indexOf(m))&&a.splice(h,1)&&f>=h&&f--},_listeners:a},d})(),ps=function(){return!io&&pn.wake()},Ge={},rA=/^[\d.\-M][\d.\-,\s]/,sA=/["']/g,oA=function(e){for(var t={},i=e.substr(1,e.length-3).split(":"),r=i[0],s=1,o=i.length,a,l,c;s<o;s++)l=i[s],a=s!==o-1?l.lastIndexOf(","):l.length,c=l.substr(0,a),t[r]=isNaN(c)?c.replace(sA,"").trim():+c,r=l.substr(a+1).trim();return t},aA=function(e){var t=e.indexOf("(")+1,i=e.indexOf(")"),r=e.indexOf("(",t);return e.substring(t,~r&&r<i?e.indexOf(")",i+1):i)},lA=function(e){var t=(e+"").split("("),i=Ge[t[0]];return i&&t.length>1&&i.config?i.config.apply(null,~e.indexOf("{")?[oA(t[1])]:aA(e).split(",").map(Pm)):Ge._CE&&rA.test(e)?Ge._CE("",e):i},qm=function(e){return function(t){return 1-e(1-t)}},Ym=function n(e,t){for(var i=e._first,r;i;)i instanceof $t?n(i,t):i.vars.yoyoEase&&(!i._yoyo||!i._repeat)&&i._yoyo!==t&&(i.timeline?n(i.timeline,t):(r=i._ease,i._ease=i._yEase,i._yEase=r,i._yoyo=t)),i=i._next},pr=function(e,t){return e&&(_t(e)?e:Ge[e]||lA(e))||t},Mr=function(e,t,i,r){i===void 0&&(i=function(l){return 1-t(1-l)}),r===void 0&&(r=function(l){return l<.5?t(l*2)/2:1-t((1-l)*2)/2});var s={easeIn:t,easeOut:i,easeInOut:r},o;return rn(e,function(a){Ge[a]=vn[a]=s,Ge[o=a.toLowerCase()]=i;for(var l in s)Ge[o+(l==="easeIn"?".in":l==="easeOut"?".out":".inOut")]=Ge[a+"."+l]=s[l]}),s},jm=function(e){return function(t){return t<.5?(1-e(1-t*2))/2:.5+e((t-.5)*2)/2}},$l=function n(e,t,i){var r=t>=1?t:1,s=(i||(e?.3:.45))/(t<1?t:1),o=s/tu*(Math.asin(1/r)||0),a=function(u){return u===1?1:r*Math.pow(2,-10*u)*F1((u-o)*s)+1},l=e==="out"?a:e==="in"?function(c){return 1-a(1-c)}:jm(a);return s=tu/s,l.config=function(c,u){return n(e,c,u)},l},ql=function n(e,t){t===void 0&&(t=1.70158);var i=function(o){return o?--o*o*((t+1)*o+t)+1:0},r=e==="out"?i:e==="in"?function(s){return 1-i(1-s)}:jm(i);return r.config=function(s){return n(e,s)},r};rn("Linear,Quad,Cubic,Quart,Quint,Strong",function(n,e){var t=e<5?e+1:e;Mr(n+",Power"+(t-1),e?function(i){return Math.pow(i,t)}:function(i){return i},function(i){return 1-Math.pow(1-i,t)},function(i){return i<.5?Math.pow(i*2,t)/2:1-Math.pow((1-i)*2,t)/2})});Ge.Linear.easeNone=Ge.none=Ge.Linear.easeIn;Mr("Elastic",$l("in"),$l("out"),$l());(function(n,e){var t=1/e,i=2*t,r=2.5*t,s=function(a){return a<t?n*a*a:a<i?n*Math.pow(a-1.5/e,2)+.75:a<r?n*(a-=2.25/e)*a+.9375:n*Math.pow(a-2.625/e,2)+.984375};Mr("Bounce",function(o){return 1-s(1-o)},s)})(7.5625,2.75);Mr("Expo",function(n){return Math.pow(2,10*(n-1))*n+n*n*n*n*n*n*(1-n)});Mr("Circ",function(n){return-(vm(1-n*n)-1)});Mr("Sine",function(n){return n===1?1:-O1(n*I1)+1});Mr("Back",ql("in"),ql("out"),ql());Ge.SteppedEase=Ge.steps=vn.SteppedEase={config:function(e,t){e===void 0&&(e=1);var i=1/e,r=e+(t?0:1),s=t?1:0,o=1-rt;return function(a){return((r*xo(0,o,a)|0)+s)*i}}};us.ease=Ge["quad.out"];rn("onComplete,onUpdate,onStart,onRepeat,onReverseComplete,onInterrupt",function(n){return ad+=n+","+n+"Params,"});var Km=function(e,t){this.id=U1++,e._gsap=this,this.target=e,this.harness=t,this.get=t?t.get:Am,this.set=t?t.getSetter:fd},ro=(function(){function n(t){this.vars=t,this._delay=+t.delay||0,(this._repeat=t.repeat===1/0?-2:t.repeat||0)&&(this._rDelay=t.repeatDelay||0,this._yoyo=!!t.yoyo||!!t.yoyoEase),this._ts=1,fs(this,+t.duration,1,1),this.data=t.data,dt&&(this._ctx=dt,dt.data.push(this)),io||pn.wake()}var e=n.prototype;return e.delay=function(i){return i||i===0?(this.parent&&this.parent.smoothChildTiming&&this.startTime(this._start+i-this._delay),this._delay=i,this):this._delay},e.duration=function(i){return arguments.length?this.totalDuration(this._repeat>0?i+(i+this._rDelay)*this._repeat:i):this.totalDuration()&&this._dur},e.totalDuration=function(i){return arguments.length?(this._dirty=0,fs(this,this._repeat<0?i:(i-this._repeat*this._rDelay)/(this._repeat+1))):this._tDur},e.totalTime=function(i,r){if(ps(),!arguments.length)return this._tTime;var s=this._dp;if(s&&s.smoothChildTiming&&this._ts){for(Xa(this,i),!s._dp||s.parent||Lm(s,this);s&&s.parent;)s.parent._time!==s._start+(s._ts>=0?s._tTime/s._ts:(s.totalDuration()-s._tTime)/-s._ts)&&s.totalTime(s._tTime,!0),s=s.parent;!this.parent&&this._dp.autoRemoveChildren&&(this._ts>0&&i<this._tDur||this._ts<0&&i>0||!this._tDur&&!i)&&Xn(this._dp,this,this._start-this._delay)}return(this._tTime!==i||!this._dur&&!r||this._initted&&Math.abs(this._zTime)===rt||!i&&!this._initted&&(this.add||this._ptLookup))&&(this._ts||(this._pTime=i),Cm(this,i,r)),this},e.time=function(i,r){return arguments.length?this.totalTime(Math.min(this.totalDuration(),i+Qh(this))%(this._dur+this._rDelay)||(i?this._dur:0),r):this._time},e.totalProgress=function(i,r){return arguments.length?this.totalTime(this.totalDuration()*i,r):this.totalDuration()?Math.min(1,this._tTime/this._tDur):this.rawTime()>=0&&this._initted?1:0},e.progress=function(i,r){return arguments.length?this.totalTime(this.duration()*(this._yoyo&&!(this.iteration()&1)?1-i:i)+Qh(this),r):this.duration()?Math.min(1,this._time/this._dur):this.rawTime()>0?1:0},e.iteration=function(i,r){var s=this.duration()+this._rDelay;return arguments.length?this.totalTime(this._time+(i-1)*s,r):this._repeat?hs(this._tTime,s)+1:1},e.timeScale=function(i,r){if(!arguments.length)return this._rts===-rt?0:this._rts;if(this._rts===i)return this;var s=this.parent&&this._ts?Aa(this.parent._time,this):this._tTime;return this._rts=+i||0,this._ts=this._ps||i===-rt?0:this._rts,this.totalTime(xo(-Math.abs(this._delay),this.totalDuration(),s),r!==!1),Wa(this),G1(this)},e.paused=function(i){return arguments.length?(this._ps!==i&&(this._ps=i,i?(this._pTime=this._tTime||Math.max(-this._delay,this.rawTime()),this._ts=this._act=0):(ps(),this._ts=this._rts,this.totalTime(this.parent&&!this.parent.smoothChildTiming?this.rawTime():this._tTime||this._pTime,this.progress()===1&&Math.abs(this._zTime)!==rt&&(this._tTime-=rt)))),this):this._ps},e.startTime=function(i){if(arguments.length){this._start=i;var r=this.parent||this._dp;return r&&(r._sort||!this.parent)&&Xn(r,this,i-this._delay),this}return this._start},e.endTime=function(i){return this._start+(nn(i)?this.totalDuration():this.duration())/Math.abs(this._ts||1)},e.rawTime=function(i){var r=this.parent||this._dp;return r?i&&(!this._ts||this._repeat&&this._time&&this.totalProgress()<1)?this._tTime%(this._dur+this._rDelay):this._ts?Aa(r.rawTime(i),this):this._tTime:this._tTime},e.revert=function(i){i===void 0&&(i=B1);var r=Ft;return Ft=i,cd(this)&&(this.timeline&&this.timeline.revert(i),this.totalTime(-.01,i.suppressEvents)),this.data!=="nested"&&i.kill!==!1&&this.kill(),Ft=r,this},e.globalTime=function(i){for(var r=this,s=arguments.length?i:r.rawTime();r;)s=r._start+s/(Math.abs(r._ts)||1),r=r._dp;return!this.parent&&this._sat?this._sat.globalTime(i):s},e.repeat=function(i){return arguments.length?(this._repeat=i===1/0?-2:i,ef(this)):this._repeat===-2?1/0:this._repeat},e.repeatDelay=function(i){if(arguments.length){var r=this._time;return this._rDelay=i,ef(this),r?this.time(r):this}return this._rDelay},e.yoyo=function(i){return arguments.length?(this._yoyo=i,this):this._yoyo},e.seek=function(i,r){return this.totalTime(Mn(this,i),nn(r))},e.restart=function(i,r){return this.play().totalTime(i?-this._delay:0,nn(r)),this._dur||(this._zTime=-rt),this},e.play=function(i,r){return i!=null&&this.seek(i,r),this.reversed(!1).paused(!1)},e.reverse=function(i,r){return i!=null&&this.seek(i||this.totalDuration(),r),this.reversed(!0).paused(!1)},e.pause=function(i,r){return i!=null&&this.seek(i,r),this.paused(!0)},e.resume=function(){return this.paused(!1)},e.reversed=function(i){return arguments.length?(!!i!==this.reversed()&&this.timeScale(-this._rts||(i?-rt:0)),this):this._rts<0},e.invalidate=function(){return this._initted=this._act=0,this._zTime=-rt,this},e.isActive=function(){var i=this.parent||this._dp,r=this._start,s;return!!(!i||this._ts&&this._initted&&i.isActive()&&(s=i.rawTime(!0))>=r&&s<this.endTime(!0)-rt)},e.eventCallback=function(i,r,s){var o=this.vars;return arguments.length>1?(r?(o[i]=r,s&&(o[i+"Params"]=s),i==="onUpdate"&&(this._onUpdate=r)):delete o[i],this):o[i]},e.then=function(i){var r=this;return new Promise(function(s){var o=_t(i)?i:Rm,a=function(){var c=r.then;r.then=null,_t(o)&&(o=o(r))&&(o.then||o===r)&&(r.then=c),s(o),r.then=c};r._initted&&r.totalProgress()===1&&r._ts>=0||!r._tTime&&r._ts<0?a():r._prom=a})},e.kill=function(){Is(this)},n})();xn(ro.prototype,{_time:0,_start:0,_end:0,_tTime:0,_tDur:0,_dirty:0,_repeat:0,_yoyo:!1,parent:null,_initted:!1,_rDelay:0,_ts:1,_dp:0,ratio:0,_zTime:-rt,_prom:0,_ps:!1,_rts:1});var $t=(function(n){_m(e,n);function e(i,r){var s;return i===void 0&&(i={}),s=n.call(this,i)||this,s.labels={},s.smoothChildTiming=!!i.smoothChildTiming,s.autoRemoveChildren=!!i.autoRemoveChildren,s._sort=nn(i.sortChildren),pt&&Xn(i.parent||pt,ui(s),r),i.reversed&&s.reverse(),i.paused&&s.paused(!0),i.scrollTrigger&&Im(ui(s),i.scrollTrigger),s}var t=e.prototype;return t.to=function(r,s,o){return Vs(0,arguments,this),this},t.from=function(r,s,o){return Vs(1,arguments,this),this},t.fromTo=function(r,s,o,a){return Vs(2,arguments,this),this},t.set=function(r,s,o){return s.duration=0,s.parent=this,zs(s).repeatDelay||(s.repeat=0),s.immediateRender=!!s.immediateRender,new Et(r,s,Mn(this,o),1),this},t.call=function(r,s,o){return Xn(this,Et.delayedCall(0,r,s),o)},t.staggerTo=function(r,s,o,a,l,c,u){return o.duration=s,o.stagger=o.stagger||a,o.onComplete=c,o.onCompleteParams=u,o.parent=this,new Et(r,o,Mn(this,l)),this},t.staggerFrom=function(r,s,o,a,l,c,u){return o.runBackwards=1,zs(o).immediateRender=nn(o.immediateRender),this.staggerTo(r,s,o,a,l,c,u)},t.staggerFromTo=function(r,s,o,a,l,c,u,d){return a.startAt=o,zs(a).immediateRender=nn(a.immediateRender),this.staggerTo(r,s,a,l,c,u,d)},t.render=function(r,s,o){var a=this._time,l=this._dirty?this.totalDuration():this._tDur,c=this._dur,u=r<=0?0:Mt(r),d=this._zTime<0!=r<0&&(this._initted||!c),p,f,_,g,m,h,v,x,w,S,C,T;if(this!==pt&&u>l&&r>=0&&(u=l),u!==this._tTime||o||d){if(a!==this._time&&c&&(u+=this._time-a,r+=this._time-a),p=u,w=this._start,x=this._ts,h=!x,d&&(c||(a=this._zTime),(r||!s)&&(this._zTime=r)),this._repeat){if(C=this._yoyo,m=c+this._rDelay,this._repeat<-1&&r<0)return this.totalTime(m*100+r,s,o);if(p=Mt(u%m),u===l?(g=this._repeat,p=c):(S=Mt(u/m),g=~~S,g&&g===S&&(p=c,g--),p>c&&(p=c)),S=hs(this._tTime,m),!a&&this._tTime&&S!==g&&this._tTime-S*m-this._dur<=0&&(S=g),C&&g&1&&(p=c-p,T=1),g!==S&&!this._lock){var A=C&&S&1,b=A===(C&&g&1);if(g<S&&(A=!A),a=A?0:u%c?c:u,this._lock=1,this.render(a||(T?0:Mt(g*m)),s,!c)._lock=0,this._tTime=u,!s&&this.parent&&mn(this,"onRepeat"),this.vars.repeatRefresh&&!T&&(this.invalidate()._lock=1),a&&a!==this._time||h!==!this._ts||this.vars.onRepeat&&!this.parent&&!this._act)return this;if(c=this._dur,l=this._tDur,b&&(this._lock=2,a=A?c:-1e-4,this.render(a,!0),this.vars.repeatRefresh&&!T&&this.invalidate()),this._lock=0,!this._ts&&!h)return this;Ym(this,T)}}if(this._hasPause&&!this._forcing&&this._lock<2&&(v=q1(this,Mt(a),Mt(p)),v&&(u-=p-(p=v._start))),this._tTime=u,this._time=p,this._act=!x,this._initted||(this._onUpdate=this.vars.onUpdate,this._initted=1,this._zTime=r,a=0),!a&&u&&!s&&!S&&(mn(this,"onStart"),this._tTime!==u))return this;if(p>=a&&r>=0)for(f=this._first;f;){if(_=f._next,(f._act||p>=f._start)&&f._ts&&v!==f){if(f.parent!==this)return this.render(r,s,o);if(f.render(f._ts>0?(p-f._start)*f._ts:(f._dirty?f.totalDuration():f._tDur)+(p-f._start)*f._ts,s,o),p!==this._time||!this._ts&&!h){v=0,_&&(u+=this._zTime=-rt);break}}f=_}else{f=this._last;for(var y=r<0?r:p;f;){if(_=f._prev,(f._act||y<=f._end)&&f._ts&&v!==f){if(f.parent!==this)return this.render(r,s,o);if(f.render(f._ts>0?(y-f._start)*f._ts:(f._dirty?f.totalDuration():f._tDur)+(y-f._start)*f._ts,s,o||Ft&&cd(f)),p!==this._time||!this._ts&&!h){v=0,_&&(u+=this._zTime=y?-rt:rt);break}}f=_}}if(v&&!s&&(this.pause(),v.render(p>=a?0:-rt)._zTime=p>=a?1:-1,this._ts))return this._start=w,Wa(this),this.render(r,s,o);this._onUpdate&&!s&&mn(this,"onUpdate",!0),(u===l&&this._tTime>=this.totalDuration()||!u&&a)&&(w===this._start||Math.abs(x)!==Math.abs(this._ts))&&(this._lock||((r||!c)&&(u===l&&this._ts>0||!u&&this._ts<0)&&Gi(this,1),!s&&!(r<0&&!a)&&(u||a||!l)&&(mn(this,u===l&&r>=0?"onComplete":"onReverseComplete",!0),this._prom&&!(u<l&&this.timeScale()>0)&&this._prom())))}return this},t.add=function(r,s){var o=this;if(xi(s)||(s=Mn(this,s,r)),!(r instanceof ro)){if(Vt(r))return r.forEach(function(a){return o.add(a,s)}),this;if(Ot(r))return this.addLabel(r,s);if(_t(r))r=Et.delayedCall(0,r);else return this}return this!==r?Xn(this,r,s):this},t.getChildren=function(r,s,o,a){r===void 0&&(r=!0),s===void 0&&(s=!0),o===void 0&&(o=!0),a===void 0&&(a=-Pn);for(var l=[],c=this._first;c;)c._start>=a&&(c instanceof Et?s&&l.push(c):(o&&l.push(c),r&&l.push.apply(l,c.getChildren(!0,s,o)))),c=c._next;return l},t.getById=function(r){for(var s=this.getChildren(1,1,1),o=s.length;o--;)if(s[o].vars.id===r)return s[o]},t.remove=function(r){return Ot(r)?this.removeLabel(r):_t(r)?this.killTweensOf(r):(r.parent===this&&Ga(this,r),r===this._recent&&(this._recent=this._last),fr(this))},t.totalTime=function(r,s){return arguments.length?(this._forcing=1,!this._dp&&this._ts&&(this._start=Mt(pn.time-(this._ts>0?r/this._ts:(this.totalDuration()-r)/-this._ts))),n.prototype.totalTime.call(this,r,s),this._forcing=0,this):this._tTime},t.addLabel=function(r,s){return this.labels[r]=Mn(this,s),this},t.removeLabel=function(r){return delete this.labels[r],this},t.addPause=function(r,s,o){var a=Et.delayedCall(0,s||to,o);return a.data="isPause",this._hasPause=1,Xn(this,a,Mn(this,r))},t.removePause=function(r){var s=this._first;for(r=Mn(this,r);s;)s._start===r&&s.data==="isPause"&&Gi(s),s=s._next},t.killTweensOf=function(r,s,o){for(var a=this.getTweensOf(r,o),l=a.length;l--;)Ii!==a[l]&&a[l].kill(r,s);return this},t.getTweensOf=function(r,s){for(var o=[],a=Rn(r),l=this._first,c=xi(s),u;l;)l instanceof Et?z1(l._targets,a)&&(c?(!Ii||l._initted&&l._ts)&&l.globalTime(0)<=s&&l.globalTime(l.totalDuration())>s:!s||l.isActive())&&o.push(l):(u=l.getTweensOf(a,s)).length&&o.push.apply(o,u),l=l._next;return o},t.tweenTo=function(r,s){s=s||{};var o=this,a=Mn(o,r),l=s,c=l.startAt,u=l.onStart,d=l.onStartParams,p=l.immediateRender,f,_=Et.to(o,xn({ease:s.ease||"none",lazy:!1,immediateRender:!1,time:a,overwrite:"auto",duration:s.duration||Math.abs((a-(c&&"time"in c?c.time:o._time))/o.timeScale())||rt,onStart:function(){if(o.pause(),!f){var m=s.duration||Math.abs((a-(c&&"time"in c?c.time:o._time))/o.timeScale());_._dur!==m&&fs(_,m,0,1).render(_._time,!0,!0),f=1}u&&u.apply(_,d||[])}},s));return p?_.render(0):_},t.tweenFromTo=function(r,s,o){return this.tweenTo(s,xn({startAt:{time:Mn(this,r)}},o))},t.recent=function(){return this._recent},t.nextLabel=function(r){return r===void 0&&(r=this._time),tf(this,Mn(this,r))},t.previousLabel=function(r){return r===void 0&&(r=this._time),tf(this,Mn(this,r),1)},t.currentLabel=function(r){return arguments.length?this.seek(r,!0):this.previousLabel(this._time+rt)},t.shiftChildren=function(r,s,o){o===void 0&&(o=0);for(var a=this._first,l=this.labels,c;a;)a._start>=o&&(a._start+=r,a._end+=r),a=a._next;if(s)for(c in l)l[c]>=o&&(l[c]+=r);return fr(this)},t.invalidate=function(r){var s=this._first;for(this._lock=0;s;)s.invalidate(r),s=s._next;return n.prototype.invalidate.call(this,r)},t.clear=function(r){r===void 0&&(r=!0);for(var s=this._first,o;s;)o=s._next,this.remove(s),s=o;return this._dp&&(this._time=this._tTime=this._pTime=0),r&&(this.labels={}),fr(this)},t.totalDuration=function(r){var s=0,o=this,a=o._last,l=Pn,c,u,d;if(arguments.length)return o.timeScale((o._repeat<0?o.duration():o.totalDuration())/(o.reversed()?-r:r));if(o._dirty){for(d=o.parent;a;)c=a._prev,a._dirty&&a.totalDuration(),u=a._start,u>l&&o._sort&&a._ts&&!o._lock?(o._lock=1,Xn(o,a,u-a._delay,1)._lock=0):l=u,u<0&&a._ts&&(s-=u,(!d&&!o._dp||d&&d.smoothChildTiming)&&(o._start+=u/o._ts,o._time-=u,o._tTime-=u),o.shiftChildren(-u,!1,-1/0),l=0),a._end>s&&a._ts&&(s=a._end),a=c;fs(o,o===pt&&o._time>s?o._time:s,1,1),o._dirty=0}return o._tDur},e.updateRoot=function(r){if(pt._ts&&(Cm(pt,Aa(r,pt)),Tm=pn.frame),pn.frame>=Zh){Zh+=gn.autoSleep||120;var s=pt._first;if((!s||!s._ts)&&gn.autoSleep&&pn._listeners.length<2){for(;s&&!s._ts;)s=s._next;s||pn.sleep()}}},e})(ro);xn($t.prototype,{_lock:0,_hasPause:0,_forcing:0});var cA=function(e,t,i,r,s,o,a){var l=new sn(this._pt,e,t,0,1,ng,null,s),c=0,u=0,d,p,f,_,g,m,h,v;for(l.b=i,l.e=r,i+="",r+="",(h=~r.indexOf("random("))&&(r=no(r)),o&&(v=[i,r],o(v,e,t),i=v[0],r=v[1]),p=i.match(Gl)||[];d=Gl.exec(r);)_=d[0],g=r.substring(c,d.index),f?f=(f+1)%5:g.substr(-5)==="rgba("&&(f=1),_!==p[u++]&&(m=parseFloat(p[u-1])||0,l._pt={_next:l._pt,p:g||u===1?g:",",s:m,c:_.charAt(1)==="="?Qr(m,_)-m:parseFloat(_)-m,m:f&&f<4?Math.round:0},c=Gl.lastIndex);return l.c=c<r.length?r.substring(c,r.length):"",l.fp=a,(ym.test(r)||h)&&(l.e=0),this._pt=l,l},ud=function(e,t,i,r,s,o,a,l,c,u){_t(r)&&(r=r(s||0,e,o));var d=e[t],p=i!=="get"?i:_t(d)?c?e[t.indexOf("set")||!_t(e["get"+t.substr(3)])?t:"get"+t.substr(3)](c):e[t]():d,f=_t(d)?c?pA:eg:hd,_;if(Ot(r)&&(~r.indexOf("random(")&&(r=no(r)),r.charAt(1)==="="&&(_=Qr(p,r)+(zt(p)||0),(_||_===0)&&(r=_))),!u||p!==r||uu)return!isNaN(p*r)&&r!==""?(_=new sn(this._pt,e,t,+p||0,r-(p||0),typeof d=="boolean"?gA:tg,0,f),c&&(_.fp=c),a&&_.modifier(a,this,e),this._pt=_):(!d&&!(t in e)&&sd(t,r),cA.call(this,e,t,p,r,f,l||gn.stringFilter,c))},uA=function(e,t,i,r,s){if(_t(e)&&(e=Hs(e,s,t,i,r)),!ni(e)||e.style&&e.nodeType||Vt(e)||xm(e))return Ot(e)?Hs(e,s,t,i,r):e;var o={},a;for(a in e)o[a]=Hs(e[a],s,t,i,r);return o},Zm=function(e,t,i,r,s,o){var a,l,c,u;if(fn[e]&&(a=new fn[e]).init(s,a.rawVars?t[e]:uA(t[e],r,s,o,i),i,r,o)!==!1&&(i._pt=l=new sn(i._pt,s,e,0,1,a.render,a,0,a.priority),i!==qr))for(c=i._ptLookup[i._targets.indexOf(s)],u=a._props.length;u--;)c[a._props[u]]=l;return a},Ii,uu,dd=function n(e,t,i){var r=e.vars,s=r.ease,o=r.startAt,a=r.immediateRender,l=r.lazy,c=r.onUpdate,u=r.runBackwards,d=r.yoyoEase,p=r.keyframes,f=r.autoRevert,_=e._dur,g=e._startAt,m=e._targets,h=e.parent,v=h&&h.data==="nested"?h.vars.targets:m,x=e._overwrite==="auto"&&!td,w=e.timeline,S,C,T,A,b,y,P,D,O,V,k,G,$;if(w&&(!p||!s)&&(s="none"),e._ease=pr(s,us.ease),e._yEase=d?qm(pr(d===!0?s:d,us.ease)):0,d&&e._yoyo&&!e._repeat&&(d=e._yEase,e._yEase=e._ease,e._ease=d),e._from=!w&&!!r.runBackwards,!w||p&&!r.stagger){if(D=m[0]?hr(m[0]).harness:0,G=D&&r[D.prop],S=Ta(r,od),g&&(g._zTime<0&&g.progress(1),t<0&&u&&a&&!f?g.render(-1,!0):g.revert(u&&_?ra:k1),g._lazy=0),o){if(Gi(e._startAt=Et.set(m,xn({data:"isStart",overwrite:!1,parent:h,immediateRender:!0,lazy:!g&&nn(l),startAt:null,delay:0,onUpdate:c&&function(){return mn(e,"onUpdate")},stagger:0},o))),e._startAt._dp=0,e._startAt._sat=e,t<0&&(Ft||!a&&!f)&&e._startAt.revert(ra),a&&_&&t<=0&&i<=0){t&&(e._zTime=t);return}}else if(u&&_&&!g){if(t&&(a=!1),T=xn({overwrite:!1,data:"isFromStart",lazy:a&&!g&&nn(l),immediateRender:a,stagger:0,parent:h},S),G&&(T[D.prop]=G),Gi(e._startAt=Et.set(m,T)),e._startAt._dp=0,e._startAt._sat=e,t<0&&(Ft?e._startAt.revert(ra):e._startAt.render(-1,!0)),e._zTime=t,!a)n(e._startAt,rt,rt);else if(!t)return}for(e._pt=e._ptCache=0,l=_&&nn(l)||l&&!_,C=0;C<m.length;C++){if(b=m[C],P=b._gsap||ld(m)[C]._gsap,e._ptLookup[C]=V={},ru[P.id]&&zi.length&&Ma(),k=v===m?C:v.indexOf(b),D&&(O=new D).init(b,G||S,e,k,v)!==!1&&(e._pt=A=new sn(e._pt,b,O.name,0,1,O.render,O,0,O.priority),O._props.forEach(function(U){V[U]=A}),O.priority&&(y=1)),!D||G)for(T in S)fn[T]&&(O=Zm(T,S,e,k,b,v))?O.priority&&(y=1):V[T]=A=ud.call(e,b,T,"get",S[T],k,v,0,r.stringFilter);e._op&&e._op[C]&&e.kill(b,e._op[C]),x&&e._pt&&(Ii=e,pt.killTweensOf(b,V,e.globalTime(t)),$=!e.parent,Ii=0),e._pt&&l&&(ru[P.id]=1)}y&&ig(e),e._onInit&&e._onInit(e)}e._onUpdate=c,e._initted=(!e._op||e._pt)&&!$,p&&t<=0&&w.render(Pn,!0,!0)},dA=function(e,t,i,r,s,o,a,l){var c=(e._pt&&e._ptCache||(e._ptCache={}))[t],u,d,p,f;if(!c)for(c=e._ptCache[t]=[],p=e._ptLookup,f=e._targets.length;f--;){if(u=p[f][t],u&&u.d&&u.d._pt)for(u=u.d._pt;u&&u.p!==t&&u.fp!==t;)u=u._next;if(!u)return uu=1,e.vars[t]="+=0",dd(e,a),uu=0,l?eo(t+" not eligible for reset"):1;c.push(u)}for(f=c.length;f--;)d=c[f],u=d._pt||d,u.s=(r||r===0)&&!s?r:u.s+(r||0)+o*u.c,u.c=i-u.s,d.e&&(d.e=wt(i)+zt(d.e)),d.b&&(d.b=u.s+zt(d.b))},hA=function(e,t){var i=e[0]?hr(e[0]).harness:0,r=i&&i.aliases,s,o,a,l;if(!r)return t;s=ds({},t);for(o in r)if(o in s)for(l=r[o].split(","),a=l.length;a--;)s[l[a]]=s[o];return s},fA=function(e,t,i,r){var s=t.ease||r||"power1.inOut",o,a;if(Vt(t))a=i[e]||(i[e]=[]),t.forEach(function(l,c){return a.push({t:c/(t.length-1)*100,v:l,e:s})});else for(o in t)a=i[o]||(i[o]=[]),o==="ease"||a.push({t:parseFloat(e),v:t[o],e:s})},Hs=function(e,t,i,r,s){return _t(e)?e.call(t,i,r,s):Ot(e)&&~e.indexOf("random(")?no(e):e},Jm=ad+"repeat,repeatDelay,yoyo,repeatRefresh,yoyoEase,autoRevert",Qm={};rn(Jm+",id,stagger,delay,duration,paused,scrollTrigger",function(n){return Qm[n]=1});var Et=(function(n){_m(e,n);function e(i,r,s,o){var a;typeof r=="number"&&(s.duration=r,r=s,s=null),a=n.call(this,o?r:zs(r))||this;var l=a.vars,c=l.duration,u=l.delay,d=l.immediateRender,p=l.stagger,f=l.overwrite,_=l.keyframes,g=l.defaults,m=l.scrollTrigger,h=l.yoyoEase,v=r.parent||pt,x=(Vt(i)||xm(i)?xi(i[0]):"length"in r)?[i]:Rn(i),w,S,C,T,A,b,y,P;if(a._targets=x.length?ld(x):eo("GSAP target "+i+" not found. https://gsap.com",!gn.nullTargetWarn)||[],a._ptLookup=[],a._overwrite=f,_||p||Ko(c)||Ko(u)){if(r=a.vars,w=a.timeline=new $t({data:"nested",defaults:g||{},targets:v&&v.data==="nested"?v.vars.targets:x}),w.kill(),w.parent=w._dp=ui(a),w._start=0,p||Ko(c)||Ko(u)){if(T=x.length,y=p&&Nm(p),ni(p))for(A in p)~Jm.indexOf(A)&&(P||(P={}),P[A]=p[A]);for(S=0;S<T;S++)C=Ta(r,Qm),C.stagger=0,h&&(C.yoyoEase=h),P&&ds(C,P),b=x[S],C.duration=+Hs(c,ui(a),S,b,x),C.delay=(+Hs(u,ui(a),S,b,x)||0)-a._delay,!p&&T===1&&C.delay&&(a._delay=u=C.delay,a._start+=u,C.delay=0),w.to(b,C,y?y(S,b,x):0),w._ease=Ge.none;w.duration()?c=u=0:a.timeline=0}else if(_){zs(xn(w.vars.defaults,{ease:"none"})),w._ease=pr(_.ease||r.ease||"none");var D=0,O,V,k;if(Vt(_))_.forEach(function(G){return w.to(x,G,">")}),w.duration();else{C={};for(A in _)A==="ease"||A==="easeEach"||fA(A,_[A],C,_.easeEach);for(A in C)for(O=C[A].sort(function(G,$){return G.t-$.t}),D=0,S=0;S<O.length;S++)V=O[S],k={ease:V.e,duration:(V.t-(S?O[S-1].t:0))/100*c},k[A]=V.v,w.to(x,k,D),D+=k.duration;w.duration()<c&&w.to({},{duration:c-w.duration()})}}c||a.duration(c=w.duration())}else a.timeline=0;return f===!0&&!td&&(Ii=ui(a),pt.killTweensOf(x),Ii=0),Xn(v,ui(a),s),r.reversed&&a.reverse(),r.paused&&a.paused(!0),(d||!c&&!_&&a._start===Mt(v._time)&&nn(d)&&W1(ui(a))&&v.data!=="nested")&&(a._tTime=-rt,a.render(Math.max(0,-u)||0)),m&&Im(ui(a),m),a}var t=e.prototype;return t.render=function(r,s,o){var a=this._time,l=this._tDur,c=this._dur,u=r<0,d=r>l-rt&&!u?l:r<rt?0:r,p,f,_,g,m,h,v,x,w;if(!c)$1(this,r,s,o);else if(d!==this._tTime||!r||o||!this._initted&&this._tTime||this._startAt&&this._zTime<0!==u||this._lazy){if(p=d,x=this.timeline,this._repeat){if(g=c+this._rDelay,this._repeat<-1&&u)return this.totalTime(g*100+r,s,o);if(p=Mt(d%g),d===l?(_=this._repeat,p=c):(m=Mt(d/g),_=~~m,_&&_===m?(p=c,_--):p>c&&(p=c)),h=this._yoyo&&_&1,h&&(w=this._yEase,p=c-p),m=hs(this._tTime,g),p===a&&!o&&this._initted&&_===m)return this._tTime=d,this;_!==m&&(x&&this._yEase&&Ym(x,h),this.vars.repeatRefresh&&!h&&!this._lock&&p!==g&&this._initted&&(this._lock=o=1,this.render(Mt(g*_),!0).invalidate()._lock=0))}if(!this._initted){if(Um(this,u?r:p,o,s,d))return this._tTime=0,this;if(a!==this._time&&!(o&&this.vars.repeatRefresh&&_!==m))return this;if(c!==this._dur)return this.render(r,s,o)}if(this._tTime=d,this._time=p,!this._act&&this._ts&&(this._act=1,this._lazy=0),this.ratio=v=(w||this._ease)(p/c),this._from&&(this.ratio=v=1-v),!a&&d&&!s&&!m&&(mn(this,"onStart"),this._tTime!==d))return this;for(f=this._pt;f;)f.r(v,f.d),f=f._next;x&&x.render(r<0?r:x._dur*x._ease(p/this._dur),s,o)||this._startAt&&(this._zTime=r),this._onUpdate&&!s&&(u&&su(this,r,s,o),mn(this,"onUpdate")),this._repeat&&_!==m&&this.vars.onRepeat&&!s&&this.parent&&mn(this,"onRepeat"),(d===this._tDur||!d)&&this._tTime===d&&(u&&!this._onUpdate&&su(this,r,!0,!0),(r||!c)&&(d===this._tDur&&this._ts>0||!d&&this._ts<0)&&Gi(this,1),!s&&!(u&&!a)&&(d||a||h)&&(mn(this,d===l?"onComplete":"onReverseComplete",!0),this._prom&&!(d<l&&this.timeScale()>0)&&this._prom()))}return this},t.targets=function(){return this._targets},t.invalidate=function(r){return(!r||!this.vars.runBackwards)&&(this._startAt=0),this._pt=this._op=this._onUpdate=this._lazy=this.ratio=0,this._ptLookup=[],this.timeline&&this.timeline.invalidate(r),n.prototype.invalidate.call(this,r)},t.resetTo=function(r,s,o,a,l){io||pn.wake(),this._ts||this.play();var c=Math.min(this._dur,(this._dp._time-this._start)*this._ts),u;return this._initted||dd(this,c),u=this._ease(c/this._dur),dA(this,r,s,o,a,u,c,l)?this.resetTo(r,s,o,a,1):(Xa(this,0),this.parent||Dm(this._dp,this,"_first","_last",this._dp._sort?"_start":0),this.render(0))},t.kill=function(r,s){if(s===void 0&&(s="all"),!r&&(!s||s==="all"))return this._lazy=this._pt=0,this.parent?Is(this):this.scrollTrigger&&this.scrollTrigger.kill(!!Ft),this;if(this.timeline){var o=this.timeline.totalDuration();return this.timeline.killTweensOf(r,s,Ii&&Ii.vars.overwrite!==!0)._first||Is(this),this.parent&&o!==this.timeline.totalDuration()&&fs(this,this._dur*this.timeline._tDur/o,0,1),this}var a=this._targets,l=r?Rn(r):a,c=this._ptLookup,u=this._pt,d,p,f,_,g,m,h;if((!s||s==="all")&&H1(a,l))return s==="all"&&(this._pt=0),Is(this);for(d=this._op=this._op||[],s!=="all"&&(Ot(s)&&(g={},rn(s,function(v){return g[v]=1}),s=g),s=hA(a,s)),h=a.length;h--;)if(~l.indexOf(a[h])){p=c[h],s==="all"?(d[h]=s,_=p,f={}):(f=d[h]=d[h]||{},_=s);for(g in _)m=p&&p[g],m&&((!("kill"in m.d)||m.d.kill(g)===!0)&&Ga(this,m,"_pt"),delete p[g]),f!=="all"&&(f[g]=1)}return this._initted&&!this._pt&&u&&Is(this),this},e.to=function(r,s){return new e(r,s,arguments[2])},e.from=function(r,s){return Vs(1,arguments)},e.delayedCall=function(r,s,o,a){return new e(s,0,{immediateRender:!1,lazy:!1,overwrite:!1,delay:r,onComplete:s,onReverseComplete:s,onCompleteParams:o,onReverseCompleteParams:o,callbackScope:a})},e.fromTo=function(r,s,o){return Vs(2,arguments)},e.set=function(r,s){return s.duration=0,s.repeatDelay||(s.repeat=0),new e(r,s)},e.killTweensOf=function(r,s,o){return pt.killTweensOf(r,s,o)},e})(ro);xn(Et.prototype,{_targets:[],_lazy:0,_startAt:0,_op:0,_onInit:0});rn("staggerTo,staggerFrom,staggerFromTo",function(n){Et[n]=function(){var e=new $t,t=au.call(arguments,0);return t.splice(n==="staggerFromTo"?5:4,0,0),e[n].apply(e,t)}});var hd=function(e,t,i){return e[t]=i},eg=function(e,t,i){return e[t](i)},pA=function(e,t,i,r){return e[t](r.fp,i)},mA=function(e,t,i){return e.setAttribute(t,i)},fd=function(e,t){return _t(e[t])?eg:nd(e[t])&&e.setAttribute?mA:hd},tg=function(e,t){return t.set(t.t,t.p,Math.round((t.s+t.c*e)*1e6)/1e6,t)},gA=function(e,t){return t.set(t.t,t.p,!!(t.s+t.c*e),t)},ng=function(e,t){var i=t._pt,r="";if(!e&&t.b)r=t.b;else if(e===1&&t.e)r=t.e;else{for(;i;)r=i.p+(i.m?i.m(i.s+i.c*e):Math.round((i.s+i.c*e)*1e4)/1e4)+r,i=i._next;r+=t.c}t.set(t.t,t.p,r,t)},pd=function(e,t){for(var i=t._pt;i;)i.r(e,i.d),i=i._next},_A=function(e,t,i,r){for(var s=this._pt,o;s;)o=s._next,s.p===r&&s.modifier(e,t,i),s=o},vA=function(e){for(var t=this._pt,i,r;t;)r=t._next,t.p===e&&!t.op||t.op===e?Ga(this,t,"_pt"):t.dep||(i=1),t=r;return!i},xA=function(e,t,i,r){r.mSet(e,t,r.m.call(r.tween,i,r.mt),r)},ig=function(e){for(var t=e._pt,i,r,s,o;t;){for(i=t._next,r=s;r&&r.pr>t.pr;)r=r._next;(t._prev=r?r._prev:o)?t._prev._next=t:s=t,(t._next=r)?r._prev=t:o=t,t=i}e._pt=s},sn=(function(){function n(t,i,r,s,o,a,l,c,u){this.t=i,this.s=s,this.c=o,this.p=r,this.r=a||tg,this.d=l||this,this.set=c||hd,this.pr=u||0,this._next=t,t&&(t._prev=this)}var e=n.prototype;return e.modifier=function(i,r,s){this.mSet=this.mSet||this.set,this.set=xA,this.m=i,this.mt=s,this.tween=r},n})();rn(ad+"parent,duration,ease,delay,overwrite,runBackwards,startAt,yoyo,immediateRender,repeat,repeatDelay,data,paused,reversed,lazy,callbackScope,stringFilter,id,yoyoEase,stagger,inherit,repeatRefresh,keyframes,autoRevert,scrollTrigger",function(n){return od[n]=1});vn.TweenMax=vn.TweenLite=Et;vn.TimelineLite=vn.TimelineMax=$t;pt=new $t({sortChildren:!1,defaults:us,autoRemoveChildren:!0,id:"root",smoothChildTiming:!0});gn.stringFilter=$m;var mr=[],oa={},wA=[],rf=0,yA=0,Yl=function(e){return(oa[e]||wA).map(function(t){return t()})},du=function(){var e=Date.now(),t=[];e-rf>2&&(Yl("matchMediaInit"),mr.forEach(function(i){var r=i.queries,s=i.conditions,o,a,l,c;for(a in r)o=Hn.matchMedia(r[a]).matches,o&&(l=1),o!==s[a]&&(s[a]=o,c=1);c&&(i.revert(),l&&t.push(i))}),Yl("matchMediaRevert"),t.forEach(function(i){return i.onMatch(i,function(r){return i.add(null,r)})}),rf=e,Yl("matchMedia"))},rg=(function(){function n(t,i){this.selector=i&&lu(i),this.data=[],this._r=[],this.isReverted=!1,this.id=yA++,t&&this.add(t)}var e=n.prototype;return e.add=function(i,r,s){_t(i)&&(s=r,r=i,i=_t);var o=this,a=function(){var c=dt,u=o.selector,d;return c&&c!==o&&c.data.push(o),s&&(o.selector=lu(s)),dt=o,d=r.apply(o,arguments),_t(d)&&o._r.push(d),dt=c,o.selector=u,o.isReverted=!1,d};return o.last=a,i===_t?a(o,function(l){return o.add(null,l)}):i?o[i]=a:a},e.ignore=function(i){var r=dt;dt=null,i(this),dt=r},e.getTweens=function(){var i=[];return this.data.forEach(function(r){return r instanceof n?i.push.apply(i,r.getTweens()):r instanceof Et&&!(r.parent&&r.parent.data==="nested")&&i.push(r)}),i},e.clear=function(){this._r.length=this.data.length=0},e.kill=function(i,r){var s=this;if(i?(function(){for(var a=s.getTweens(),l=s.data.length,c;l--;)c=s.data[l],c.data==="isFlip"&&(c.revert(),c.getChildren(!0,!0,!1).forEach(function(u){return a.splice(a.indexOf(u),1)}));for(a.map(function(u){return{g:u._dur||u._delay||u._sat&&!u._sat.vars.immediateRender?u.globalTime(0):-1/0,t:u}}).sort(function(u,d){return d.g-u.g||-1/0}).forEach(function(u){return u.t.revert(i)}),l=s.data.length;l--;)c=s.data[l],c instanceof $t?c.data!=="nested"&&(c.scrollTrigger&&c.scrollTrigger.revert(),c.kill()):!(c instanceof Et)&&c.revert&&c.revert(i);s._r.forEach(function(u){return u(i,s)}),s.isReverted=!0})():this.data.forEach(function(a){return a.kill&&a.kill()}),this.clear(),r)for(var o=mr.length;o--;)mr[o].id===this.id&&mr.splice(o,1)},e.revert=function(i){this.kill(i||{})},n})(),bA=(function(){function n(t){this.contexts=[],this.scope=t,dt&&dt.data.push(this)}var e=n.prototype;return e.add=function(i,r,s){ni(i)||(i={matches:i});var o=new rg(0,s||this.scope),a=o.conditions={},l,c,u;dt&&!o.selector&&(o.selector=dt.selector),this.contexts.push(o),r=o.add("onMatch",r),o.queries=i;for(c in i)c==="all"?u=1:(l=Hn.matchMedia(i[c]),l&&(mr.indexOf(o)<0&&mr.push(o),(a[c]=l.matches)&&(u=1),l.addListener?l.addListener(du):l.addEventListener("change",du)));return u&&r(o,function(d){return o.add(null,d)}),this},e.revert=function(i){this.kill(i||{})},e.kill=function(i){this.contexts.forEach(function(r){return r.kill(i,!0)})},n})(),Ca={registerPlugin:function(){for(var e=arguments.length,t=new Array(e),i=0;i<e;i++)t[i]=arguments[i];t.forEach(function(r){return Gm(r)})},timeline:function(e){return new $t(e)},getTweensOf:function(e,t){return pt.getTweensOf(e,t)},getProperty:function(e,t,i,r){Ot(e)&&(e=Rn(e)[0]);var s=hr(e||{}).get,o=i?Rm:Pm;return i==="native"&&(i=""),e&&(t?o((fn[t]&&fn[t].get||s)(e,t,i,r)):function(a,l,c){return o((fn[a]&&fn[a].get||s)(e,a,l,c))})},quickSetter:function(e,t,i){if(e=Rn(e),e.length>1){var r=e.map(function(u){return an.quickSetter(u,t,i)}),s=r.length;return function(u){for(var d=s;d--;)r[d](u)}}e=e[0]||{};var o=fn[t],a=hr(e),l=a.harness&&(a.harness.aliases||{})[t]||t,c=o?function(u){var d=new o;qr._pt=0,d.init(e,i?u+i:u,qr,0,[e]),d.render(1,d),qr._pt&&pd(1,qr)}:a.set(e,l);return o?c:function(u){return c(e,l,i?u+i:u,a,1)}},quickTo:function(e,t,i){var r,s=an.to(e,xn((r={},r[t]="+=0.1",r.paused=!0,r.stagger=0,r),i||{})),o=function(l,c,u){return s.resetTo(t,l,c,u)};return o.tween=s,o},isTweening:function(e){return pt.getTweensOf(e,!0).length>0},defaults:function(e){return e&&e.ease&&(e.ease=pr(e.ease,us.ease)),Jh(us,e||{})},config:function(e){return Jh(gn,e||{})},registerEffect:function(e){var t=e.name,i=e.effect,r=e.plugins,s=e.defaults,o=e.extendTimeline;(r||"").split(",").forEach(function(a){return a&&!fn[a]&&!vn[a]&&eo(t+" effect requires "+a+" plugin.")}),Wl[t]=function(a,l,c){return i(Rn(a),xn(l||{},s),c)},o&&($t.prototype[t]=function(a,l,c){return this.add(Wl[t](a,ni(l)?l:(c=l)&&{},this),c)})},registerEase:function(e,t){Ge[e]=pr(t)},parseEase:function(e,t){return arguments.length?pr(e,t):Ge},getById:function(e){return pt.getById(e)},exportRoot:function(e,t){e===void 0&&(e={});var i=new $t(e),r,s;for(i.smoothChildTiming=nn(e.smoothChildTiming),pt.remove(i),i._dp=0,i._time=i._tTime=pt._time,r=pt._first;r;)s=r._next,(t||!(!r._dur&&r instanceof Et&&r.vars.onComplete===r._targets[0]))&&Xn(i,r,r._start-r._delay),r=s;return Xn(pt,i,0),i},context:function(e,t){return e?new rg(e,t):dt},matchMedia:function(e){return new bA(e)},matchMediaRefresh:function(){return mr.forEach(function(e){var t=e.conditions,i,r;for(r in t)t[r]&&(t[r]=!1,i=1);i&&e.revert()})||du()},addEventListener:function(e,t){var i=oa[e]||(oa[e]=[]);~i.indexOf(t)||i.push(t)},removeEventListener:function(e,t){var i=oa[e],r=i&&i.indexOf(t);r>=0&&i.splice(r,1)},utils:{wrap:eA,wrapYoyo:tA,distribute:Nm,random:Bm,snap:km,normalize:Q1,getUnit:zt,clamp:j1,splitColor:Wm,toArray:Rn,selector:lu,mapRange:Vm,pipe:Z1,unitize:J1,interpolate:nA,shuffle:Fm},install:Em,effects:Wl,ticker:pn,updateRoot:$t.updateRoot,plugins:fn,globalTimeline:pt,core:{PropTween:sn,globals:Mm,Tween:Et,Timeline:$t,Animation:ro,getCache:hr,_removeLinkedListItem:Ga,reverting:function(){return Ft},context:function(e){return e&&dt&&(dt.data.push(e),e._ctx=dt),dt},suppressOverwrites:function(e){return td=e}}};rn("to,from,fromTo,delayedCall,set,killTweensOf",function(n){return Ca[n]=Et[n]});pn.add($t.updateRoot);qr=Ca.to({},{duration:0});var SA=function(e,t){for(var i=e._pt;i&&i.p!==t&&i.op!==t&&i.fp!==t;)i=i._next;return i},EA=function(e,t){var i=e._targets,r,s,o;for(r in t)for(s=i.length;s--;)o=e._ptLookup[s][r],o&&(o=o.d)&&(o._pt&&(o=SA(o,r)),o&&o.modifier&&o.modifier(t[r],e,i[s],r))},jl=function(e,t){return{name:e,headless:1,rawVars:1,init:function(r,s,o){o._onInit=function(a){var l,c;if(Ot(s)&&(l={},rn(s,function(u){return l[u]=1}),s=l),t){l={};for(c in s)l[c]=t(s[c]);s=l}EA(a,s)}}}},an=Ca.registerPlugin({name:"attr",init:function(e,t,i,r,s){var o,a,l;this.tween=i;for(o in t)l=e.getAttribute(o)||"",a=this.add(e,"setAttribute",(l||0)+"",t[o],r,s,0,0,o),a.op=o,a.b=l,this._props.push(o)},render:function(e,t){for(var i=t._pt;i;)Ft?i.set(i.t,i.p,i.b,i):i.r(e,i.d),i=i._next}},{name:"endArray",headless:1,init:function(e,t){for(var i=t.length;i--;)this.add(e,i,e[i]||0,t[i],0,0,0,0,0,1)}},jl("roundProps",cu),jl("modifiers"),jl("snap",km))||Ca;Et.version=$t.version=an.version="3.13.0";Sm=1;id()&&ps();Ge.Power0;Ge.Power1;Ge.Power2;Ge.Power3;Ge.Power4;Ge.Linear;Ge.Quad;Ge.Cubic;Ge.Quart;Ge.Quint;Ge.Strong;Ge.Elastic;Ge.Back;Ge.SteppedEase;Ge.Bounce;Ge.Sine;Ge.Expo;Ge.Circ;/*!
 * CSSPlugin 3.13.0
 * https://gsap.com
 *
 * Copyright 2008-2025, GreenSock. All rights reserved.
 * Subject to the terms at https://gsap.com/standard-license
 * @author: Jack Doyle, jack@greensock.com
*/var sf,Ui,es,md,ur,of,gd,MA=function(){return typeof window<"u"},wi={},rr=180/Math.PI,ts=Math.PI/180,Hr=Math.atan2,af=1e8,_d=/([A-Z])/g,TA=/(left|right|width|margin|padding|x)/i,AA=/[\s,\(]\S/,Kn={autoAlpha:"opacity,visibility",scale:"scaleX,scaleY",alpha:"opacity"},hu=function(e,t){return t.set(t.t,t.p,Math.round((t.s+t.c*e)*1e4)/1e4+t.u,t)},CA=function(e,t){return t.set(t.t,t.p,e===1?t.e:Math.round((t.s+t.c*e)*1e4)/1e4+t.u,t)},PA=function(e,t){return t.set(t.t,t.p,e?Math.round((t.s+t.c*e)*1e4)/1e4+t.u:t.b,t)},RA=function(e,t){var i=t.s+t.c*e;t.set(t.t,t.p,~~(i+(i<0?-.5:.5))+t.u,t)},sg=function(e,t){return t.set(t.t,t.p,e?t.e:t.b,t)},og=function(e,t){return t.set(t.t,t.p,e!==1?t.b:t.e,t)},DA=function(e,t,i){return e.style[t]=i},LA=function(e,t,i){return e.style.setProperty(t,i)},IA=function(e,t,i){return e._gsap[t]=i},UA=function(e,t,i){return e._gsap.scaleX=e._gsap.scaleY=i},OA=function(e,t,i,r,s){var o=e._gsap;o.scaleX=o.scaleY=i,o.renderTransform(s,o)},FA=function(e,t,i,r,s){var o=e._gsap;o[t]=i,o.renderTransform(s,o)},mt="transform",on=mt+"Origin",NA=function n(e,t){var i=this,r=this.target,s=r.style,o=r._gsap;if(e in wi&&s){if(this.tfm=this.tfm||{},e!=="transform")e=Kn[e]||e,~e.indexOf(",")?e.split(",").forEach(function(a){return i.tfm[a]=di(r,a)}):this.tfm[e]=o.x?o[e]:di(r,e),e===on&&(this.tfm.zOrigin=o.zOrigin);else return Kn.transform.split(",").forEach(function(a){return n.call(i,a,t)});if(this.props.indexOf(mt)>=0)return;o.svg&&(this.svgo=r.getAttribute("data-svg-origin"),this.props.push(on,t,"")),e=mt}(s||t)&&this.props.push(e,t,s[e])},ag=function(e){e.translate&&(e.removeProperty("translate"),e.removeProperty("scale"),e.removeProperty("rotate"))},kA=function(){var e=this.props,t=this.target,i=t.style,r=t._gsap,s,o;for(s=0;s<e.length;s+=3)e[s+1]?e[s+1]===2?t[e[s]](e[s+2]):t[e[s]]=e[s+2]:e[s+2]?i[e[s]]=e[s+2]:i.removeProperty(e[s].substr(0,2)==="--"?e[s]:e[s].replace(_d,"-$1").toLowerCase());if(this.tfm){for(o in this.tfm)r[o]=this.tfm[o];r.svg&&(r.renderTransform(),t.setAttribute("data-svg-origin",this.svgo||"")),s=gd(),(!s||!s.isStart)&&!i[mt]&&(ag(i),r.zOrigin&&i[on]&&(i[on]+=" "+r.zOrigin+"px",r.zOrigin=0,r.renderTransform()),r.uncache=1)}},lg=function(e,t){var i={target:e,props:[],revert:kA,save:NA};return e._gsap||an.core.getCache(e),t&&e.style&&e.nodeType&&t.split(",").forEach(function(r){return i.save(r)}),i},cg,fu=function(e,t){var i=Ui.createElementNS?Ui.createElementNS((t||"http://www.w3.org/1999/xhtml").replace(/^https/,"http"),e):Ui.createElement(e);return i&&i.style?i:Ui.createElement(e)},Dn=function n(e,t,i){var r=getComputedStyle(e);return r[t]||r.getPropertyValue(t.replace(_d,"-$1").toLowerCase())||r.getPropertyValue(t)||!i&&n(e,ms(t)||t,1)||""},lf="O,Moz,ms,Ms,Webkit".split(","),ms=function(e,t,i){var r=t||ur,s=r.style,o=5;if(e in s&&!i)return e;for(e=e.charAt(0).toUpperCase()+e.substr(1);o--&&!(lf[o]+e in s););return o<0?null:(o===3?"ms":o>=0?lf[o]:"")+e},pu=function(){MA()&&window.document&&(sf=window,Ui=sf.document,es=Ui.documentElement,ur=fu("div")||{style:{}},fu("div"),mt=ms(mt),on=mt+"Origin",ur.style.cssText="border-width:0;line-height:0;position:absolute;padding:0",cg=!!ms("perspective"),gd=an.core.reverting,md=1)},cf=function(e){var t=e.ownerSVGElement,i=fu("svg",t&&t.getAttribute("xmlns")||"http://www.w3.org/2000/svg"),r=e.cloneNode(!0),s;r.style.display="block",i.appendChild(r),es.appendChild(i);try{s=r.getBBox()}catch{}return i.removeChild(r),es.removeChild(i),s},uf=function(e,t){for(var i=t.length;i--;)if(e.hasAttribute(t[i]))return e.getAttribute(t[i])},ug=function(e){var t,i;try{t=e.getBBox()}catch{t=cf(e),i=1}return t&&(t.width||t.height)||i||(t=cf(e)),t&&!t.width&&!t.x&&!t.y?{x:+uf(e,["x","cx","x1"])||0,y:+uf(e,["y","cy","y1"])||0,width:0,height:0}:t},dg=function(e){return!!(e.getCTM&&(!e.parentNode||e.ownerSVGElement)&&ug(e))},wr=function(e,t){if(t){var i=e.style,r;t in wi&&t!==on&&(t=mt),i.removeProperty?(r=t.substr(0,2),(r==="ms"||t.substr(0,6)==="webkit")&&(t="-"+t),i.removeProperty(r==="--"?t:t.replace(_d,"-$1").toLowerCase())):i.removeAttribute(t)}},Oi=function(e,t,i,r,s,o){var a=new sn(e._pt,t,i,0,1,o?og:sg);return e._pt=a,a.b=r,a.e=s,e._props.push(i),a},df={deg:1,rad:1,turn:1},BA={grid:1,flex:1},Wi=function n(e,t,i,r){var s=parseFloat(i)||0,o=(i+"").trim().substr((s+"").length)||"px",a=ur.style,l=TA.test(t),c=e.tagName.toLowerCase()==="svg",u=(c?"client":"offset")+(l?"Width":"Height"),d=100,p=r==="px",f=r==="%",_,g,m,h;if(r===o||!s||df[r]||df[o])return s;if(o!=="px"&&!p&&(s=n(e,t,i,"px")),h=e.getCTM&&dg(e),(f||o==="%")&&(wi[t]||~t.indexOf("adius")))return _=h?e.getBBox()[l?"width":"height"]:e[u],wt(f?s/_*d:s/100*_);if(a[l?"width":"height"]=d+(p?o:r),g=r!=="rem"&&~t.indexOf("adius")||r==="em"&&e.appendChild&&!c?e:e.parentNode,h&&(g=(e.ownerSVGElement||{}).parentNode),(!g||g===Ui||!g.appendChild)&&(g=Ui.body),m=g._gsap,m&&f&&m.width&&l&&m.time===pn.time&&!m.uncache)return wt(s/m.width*d);if(f&&(t==="height"||t==="width")){var v=e.style[t];e.style[t]=d+r,_=e[u],v?e.style[t]=v:wr(e,t)}else(f||o==="%")&&!BA[Dn(g,"display")]&&(a.position=Dn(e,"position")),g===e&&(a.position="static"),g.appendChild(ur),_=ur[u],g.removeChild(ur),a.position="absolute";return l&&f&&(m=hr(g),m.time=pn.time,m.width=g[u]),wt(p?_*s/d:_&&s?d/_*s:0)},di=function(e,t,i,r){var s;return md||pu(),t in Kn&&t!=="transform"&&(t=Kn[t],~t.indexOf(",")&&(t=t.split(",")[0])),wi[t]&&t!=="transform"?(s=oo(e,r),s=t!=="transformOrigin"?s[t]:s.svg?s.origin:Ra(Dn(e,on))+" "+s.zOrigin+"px"):(s=e.style[t],(!s||s==="auto"||r||~(s+"").indexOf("calc("))&&(s=Pa[t]&&Pa[t](e,t,i)||Dn(e,t)||Am(e,t)||(t==="opacity"?1:0))),i&&!~(s+"").trim().indexOf(" ")?Wi(e,t,s,i)+i:s},zA=function(e,t,i,r){if(!i||i==="none"){var s=ms(t,e,1),o=s&&Dn(e,s,1);o&&o!==i?(t=s,i=o):t==="borderColor"&&(i=Dn(e,"borderTopColor"))}var a=new sn(this._pt,e.style,t,0,1,ng),l=0,c=0,u,d,p,f,_,g,m,h,v,x,w,S;if(a.b=i,a.e=r,i+="",r+="",r.substring(0,6)==="var(--"&&(r=Dn(e,r.substring(4,r.indexOf(")")))),r==="auto"&&(g=e.style[t],e.style[t]=r,r=Dn(e,t)||r,g?e.style[t]=g:wr(e,t)),u=[i,r],$m(u),i=u[0],r=u[1],p=i.match($r)||[],S=r.match($r)||[],S.length){for(;d=$r.exec(r);)m=d[0],v=r.substring(l,d.index),_?_=(_+1)%5:(v.substr(-5)==="rgba("||v.substr(-5)==="hsla(")&&(_=1),m!==(g=p[c++]||"")&&(f=parseFloat(g)||0,w=g.substr((f+"").length),m.charAt(1)==="="&&(m=Qr(f,m)+w),h=parseFloat(m),x=m.substr((h+"").length),l=$r.lastIndex-x.length,x||(x=x||gn.units[t]||w,l===r.length&&(r+=x,a.e+=x)),w!==x&&(f=Wi(e,t,g,x)||0),a._pt={_next:a._pt,p:v||c===1?v:",",s:f,c:h-f,m:_&&_<4||t==="zIndex"?Math.round:0});a.c=l<r.length?r.substring(l,r.length):""}else a.r=t==="display"&&r==="none"?og:sg;return ym.test(r)&&(a.e=0),this._pt=a,a},hf={top:"0%",bottom:"100%",left:"0%",right:"100%",center:"50%"},VA=function(e){var t=e.split(" "),i=t[0],r=t[1]||"50%";return(i==="top"||i==="bottom"||r==="left"||r==="right")&&(e=i,i=r,r=e),t[0]=hf[i]||i,t[1]=hf[r]||r,t.join(" ")},HA=function(e,t){if(t.tween&&t.tween._time===t.tween._dur){var i=t.t,r=i.style,s=t.u,o=i._gsap,a,l,c;if(s==="all"||s===!0)r.cssText="",l=1;else for(s=s.split(","),c=s.length;--c>-1;)a=s[c],wi[a]&&(l=1,a=a==="transformOrigin"?on:mt),wr(i,a);l&&(wr(i,mt),o&&(o.svg&&i.removeAttribute("transform"),r.scale=r.rotate=r.translate="none",oo(i,1),o.uncache=1,ag(r)))}},Pa={clearProps:function(e,t,i,r,s){if(s.data!=="isFromStart"){var o=e._pt=new sn(e._pt,t,i,0,0,HA);return o.u=r,o.pr=-10,o.tween=s,e._props.push(i),1}}},so=[1,0,0,1,0,0],hg={},fg=function(e){return e==="matrix(1, 0, 0, 1, 0, 0)"||e==="none"||!e},ff=function(e){var t=Dn(e,mt);return fg(t)?so:t.substr(7).match(wm).map(wt)},vd=function(e,t){var i=e._gsap||hr(e),r=e.style,s=ff(e),o,a,l,c;return i.svg&&e.getAttribute("transform")?(l=e.transform.baseVal.consolidate().matrix,s=[l.a,l.b,l.c,l.d,l.e,l.f],s.join(",")==="1,0,0,1,0,0"?so:s):(s===so&&!e.offsetParent&&e!==es&&!i.svg&&(l=r.display,r.display="block",o=e.parentNode,(!o||!e.offsetParent&&!e.getBoundingClientRect().width)&&(c=1,a=e.nextElementSibling,es.appendChild(e)),s=ff(e),l?r.display=l:wr(e,"display"),c&&(a?o.insertBefore(e,a):o?o.appendChild(e):es.removeChild(e))),t&&s.length>6?[s[0],s[1],s[4],s[5],s[12],s[13]]:s)},mu=function(e,t,i,r,s,o){var a=e._gsap,l=s||vd(e,!0),c=a.xOrigin||0,u=a.yOrigin||0,d=a.xOffset||0,p=a.yOffset||0,f=l[0],_=l[1],g=l[2],m=l[3],h=l[4],v=l[5],x=t.split(" "),w=parseFloat(x[0])||0,S=parseFloat(x[1])||0,C,T,A,b;i?l!==so&&(T=f*m-_*g)&&(A=w*(m/T)+S*(-g/T)+(g*v-m*h)/T,b=w*(-_/T)+S*(f/T)-(f*v-_*h)/T,w=A,S=b):(C=ug(e),w=C.x+(~x[0].indexOf("%")?w/100*C.width:w),S=C.y+(~(x[1]||x[0]).indexOf("%")?S/100*C.height:S)),r||r!==!1&&a.smooth?(h=w-c,v=S-u,a.xOffset=d+(h*f+v*g)-h,a.yOffset=p+(h*_+v*m)-v):a.xOffset=a.yOffset=0,a.xOrigin=w,a.yOrigin=S,a.smooth=!!r,a.origin=t,a.originIsAbsolute=!!i,e.style[on]="0px 0px",o&&(Oi(o,a,"xOrigin",c,w),Oi(o,a,"yOrigin",u,S),Oi(o,a,"xOffset",d,a.xOffset),Oi(o,a,"yOffset",p,a.yOffset)),e.setAttribute("data-svg-origin",w+" "+S)},oo=function(e,t){var i=e._gsap||new Km(e);if("x"in i&&!t&&!i.uncache)return i;var r=e.style,s=i.scaleX<0,o="px",a="deg",l=getComputedStyle(e),c=Dn(e,on)||"0",u,d,p,f,_,g,m,h,v,x,w,S,C,T,A,b,y,P,D,O,V,k,G,$,U,Z,ee,ce,Ae,Je,We,ze;return u=d=p=g=m=h=v=x=w=0,f=_=1,i.svg=!!(e.getCTM&&dg(e)),l.translate&&((l.translate!=="none"||l.scale!=="none"||l.rotate!=="none")&&(r[mt]=(l.translate!=="none"?"translate3d("+(l.translate+" 0 0").split(" ").slice(0,3).join(", ")+") ":"")+(l.rotate!=="none"?"rotate("+l.rotate+") ":"")+(l.scale!=="none"?"scale("+l.scale.split(" ").join(",")+") ":"")+(l[mt]!=="none"?l[mt]:"")),r.scale=r.rotate=r.translate="none"),T=vd(e,i.svg),i.svg&&(i.uncache?(U=e.getBBox(),c=i.xOrigin-U.x+"px "+(i.yOrigin-U.y)+"px",$=""):$=!t&&e.getAttribute("data-svg-origin"),mu(e,$||c,!!$||i.originIsAbsolute,i.smooth!==!1,T)),S=i.xOrigin||0,C=i.yOrigin||0,T!==so&&(P=T[0],D=T[1],O=T[2],V=T[3],u=k=T[4],d=G=T[5],T.length===6?(f=Math.sqrt(P*P+D*D),_=Math.sqrt(V*V+O*O),g=P||D?Hr(D,P)*rr:0,v=O||V?Hr(O,V)*rr+g:0,v&&(_*=Math.abs(Math.cos(v*ts))),i.svg&&(u-=S-(S*P+C*O),d-=C-(S*D+C*V))):(ze=T[6],Je=T[7],ee=T[8],ce=T[9],Ae=T[10],We=T[11],u=T[12],d=T[13],p=T[14],A=Hr(ze,Ae),m=A*rr,A&&(b=Math.cos(-A),y=Math.sin(-A),$=k*b+ee*y,U=G*b+ce*y,Z=ze*b+Ae*y,ee=k*-y+ee*b,ce=G*-y+ce*b,Ae=ze*-y+Ae*b,We=Je*-y+We*b,k=$,G=U,ze=Z),A=Hr(-O,Ae),h=A*rr,A&&(b=Math.cos(-A),y=Math.sin(-A),$=P*b-ee*y,U=D*b-ce*y,Z=O*b-Ae*y,We=V*y+We*b,P=$,D=U,O=Z),A=Hr(D,P),g=A*rr,A&&(b=Math.cos(A),y=Math.sin(A),$=P*b+D*y,U=k*b+G*y,D=D*b-P*y,G=G*b-k*y,P=$,k=U),m&&Math.abs(m)+Math.abs(g)>359.9&&(m=g=0,h=180-h),f=wt(Math.sqrt(P*P+D*D+O*O)),_=wt(Math.sqrt(G*G+ze*ze)),A=Hr(k,G),v=Math.abs(A)>2e-4?A*rr:0,w=We?1/(We<0?-We:We):0),i.svg&&($=e.getAttribute("transform"),i.forceCSS=e.setAttribute("transform","")||!fg(Dn(e,mt)),$&&e.setAttribute("transform",$))),Math.abs(v)>90&&Math.abs(v)<270&&(s?(f*=-1,v+=g<=0?180:-180,g+=g<=0?180:-180):(_*=-1,v+=v<=0?180:-180)),t=t||i.uncache,i.x=u-((i.xPercent=u&&(!t&&i.xPercent||(Math.round(e.offsetWidth/2)===Math.round(-u)?-50:0)))?e.offsetWidth*i.xPercent/100:0)+o,i.y=d-((i.yPercent=d&&(!t&&i.yPercent||(Math.round(e.offsetHeight/2)===Math.round(-d)?-50:0)))?e.offsetHeight*i.yPercent/100:0)+o,i.z=p+o,i.scaleX=wt(f),i.scaleY=wt(_),i.rotation=wt(g)+a,i.rotationX=wt(m)+a,i.rotationY=wt(h)+a,i.skewX=v+a,i.skewY=x+a,i.transformPerspective=w+o,(i.zOrigin=parseFloat(c.split(" ")[2])||!t&&i.zOrigin||0)&&(r[on]=Ra(c)),i.xOffset=i.yOffset=0,i.force3D=gn.force3D,i.renderTransform=i.svg?WA:cg?pg:GA,i.uncache=0,i},Ra=function(e){return(e=e.split(" "))[0]+" "+e[1]},Kl=function(e,t,i){var r=zt(t);return wt(parseFloat(t)+parseFloat(Wi(e,"x",i+"px",r)))+r},GA=function(e,t){t.z="0px",t.rotationY=t.rotationX="0deg",t.force3D=0,pg(e,t)},tr="0deg",Ds="0px",nr=") ",pg=function(e,t){var i=t||this,r=i.xPercent,s=i.yPercent,o=i.x,a=i.y,l=i.z,c=i.rotation,u=i.rotationY,d=i.rotationX,p=i.skewX,f=i.skewY,_=i.scaleX,g=i.scaleY,m=i.transformPerspective,h=i.force3D,v=i.target,x=i.zOrigin,w="",S=h==="auto"&&e&&e!==1||h===!0;if(x&&(d!==tr||u!==tr)){var C=parseFloat(u)*ts,T=Math.sin(C),A=Math.cos(C),b;C=parseFloat(d)*ts,b=Math.cos(C),o=Kl(v,o,T*b*-x),a=Kl(v,a,-Math.sin(C)*-x),l=Kl(v,l,A*b*-x+x)}m!==Ds&&(w+="perspective("+m+nr),(r||s)&&(w+="translate("+r+"%, "+s+"%) "),(S||o!==Ds||a!==Ds||l!==Ds)&&(w+=l!==Ds||S?"translate3d("+o+", "+a+", "+l+") ":"translate("+o+", "+a+nr),c!==tr&&(w+="rotate("+c+nr),u!==tr&&(w+="rotateY("+u+nr),d!==tr&&(w+="rotateX("+d+nr),(p!==tr||f!==tr)&&(w+="skew("+p+", "+f+nr),(_!==1||g!==1)&&(w+="scale("+_+", "+g+nr),v.style[mt]=w||"translate(0, 0)"},WA=function(e,t){var i=t||this,r=i.xPercent,s=i.yPercent,o=i.x,a=i.y,l=i.rotation,c=i.skewX,u=i.skewY,d=i.scaleX,p=i.scaleY,f=i.target,_=i.xOrigin,g=i.yOrigin,m=i.xOffset,h=i.yOffset,v=i.forceCSS,x=parseFloat(o),w=parseFloat(a),S,C,T,A,b;l=parseFloat(l),c=parseFloat(c),u=parseFloat(u),u&&(u=parseFloat(u),c+=u,l+=u),l||c?(l*=ts,c*=ts,S=Math.cos(l)*d,C=Math.sin(l)*d,T=Math.sin(l-c)*-p,A=Math.cos(l-c)*p,c&&(u*=ts,b=Math.tan(c-u),b=Math.sqrt(1+b*b),T*=b,A*=b,u&&(b=Math.tan(u),b=Math.sqrt(1+b*b),S*=b,C*=b)),S=wt(S),C=wt(C),T=wt(T),A=wt(A)):(S=d,A=p,C=T=0),(x&&!~(o+"").indexOf("px")||w&&!~(a+"").indexOf("px"))&&(x=Wi(f,"x",o,"px"),w=Wi(f,"y",a,"px")),(_||g||m||h)&&(x=wt(x+_-(_*S+g*T)+m),w=wt(w+g-(_*C+g*A)+h)),(r||s)&&(b=f.getBBox(),x=wt(x+r/100*b.width),w=wt(w+s/100*b.height)),b="matrix("+S+","+C+","+T+","+A+","+x+","+w+")",f.setAttribute("transform",b),v&&(f.style[mt]=b)},XA=function(e,t,i,r,s){var o=360,a=Ot(s),l=parseFloat(s)*(a&&~s.indexOf("rad")?rr:1),c=l-r,u=r+c+"deg",d,p;return a&&(d=s.split("_")[1],d==="short"&&(c%=o,c!==c%(o/2)&&(c+=c<0?o:-o)),d==="cw"&&c<0?c=(c+o*af)%o-~~(c/o)*o:d==="ccw"&&c>0&&(c=(c-o*af)%o-~~(c/o)*o)),e._pt=p=new sn(e._pt,t,i,r,c,CA),p.e=u,p.u="deg",e._props.push(i),p},pf=function(e,t){for(var i in t)e[i]=t[i];return e},$A=function(e,t,i){var r=pf({},i._gsap),s="perspective,force3D,transformOrigin,svgOrigin",o=i.style,a,l,c,u,d,p,f,_;r.svg?(c=i.getAttribute("transform"),i.setAttribute("transform",""),o[mt]=t,a=oo(i,1),wr(i,mt),i.setAttribute("transform",c)):(c=getComputedStyle(i)[mt],o[mt]=t,a=oo(i,1),o[mt]=c);for(l in wi)c=r[l],u=a[l],c!==u&&s.indexOf(l)<0&&(f=zt(c),_=zt(u),d=f!==_?Wi(i,l,c,_):parseFloat(c),p=parseFloat(u),e._pt=new sn(e._pt,a,l,d,p-d,hu),e._pt.u=_||0,e._props.push(l));pf(a,r)};rn("padding,margin,Width,Radius",function(n,e){var t="Top",i="Right",r="Bottom",s="Left",o=(e<3?[t,i,r,s]:[t+s,t+i,r+i,r+s]).map(function(a){return e<2?n+a:"border"+a+n});Pa[e>1?"border"+n:n]=function(a,l,c,u,d){var p,f;if(arguments.length<4)return p=o.map(function(_){return di(a,_,c)}),f=p.join(" "),f.split(p[0]).length===5?p[0]:f;p=(u+"").split(" "),f={},o.forEach(function(_,g){return f[_]=p[g]=p[g]||p[(g-1)/2|0]}),a.init(l,f,d)}});var mg={name:"css",register:pu,targetTest:function(e){return e.style&&e.nodeType},init:function(e,t,i,r,s){var o=this._props,a=e.style,l=i.vars.startAt,c,u,d,p,f,_,g,m,h,v,x,w,S,C,T,A;md||pu(),this.styles=this.styles||lg(e),A=this.styles.props,this.tween=i;for(g in t)if(g!=="autoRound"&&(u=t[g],!(fn[g]&&Zm(g,t,i,r,e,s)))){if(f=typeof u,_=Pa[g],f==="function"&&(u=u.call(i,r,e,s),f=typeof u),f==="string"&&~u.indexOf("random(")&&(u=no(u)),_)_(this,e,g,u,i)&&(T=1);else if(g.substr(0,2)==="--")c=(getComputedStyle(e).getPropertyValue(g)+"").trim(),u+="",Vi.lastIndex=0,Vi.test(c)||(m=zt(c),h=zt(u)),h?m!==h&&(c=Wi(e,g,c,h)+h):m&&(u+=m),this.add(a,"setProperty",c,u,r,s,0,0,g),o.push(g),A.push(g,0,a[g]);else if(f!=="undefined"){if(l&&g in l?(c=typeof l[g]=="function"?l[g].call(i,r,e,s):l[g],Ot(c)&&~c.indexOf("random(")&&(c=no(c)),zt(c+"")||c==="auto"||(c+=gn.units[g]||zt(di(e,g))||""),(c+"").charAt(1)==="="&&(c=di(e,g))):c=di(e,g),p=parseFloat(c),v=f==="string"&&u.charAt(1)==="="&&u.substr(0,2),v&&(u=u.substr(2)),d=parseFloat(u),g in Kn&&(g==="autoAlpha"&&(p===1&&di(e,"visibility")==="hidden"&&d&&(p=0),A.push("visibility",0,a.visibility),Oi(this,a,"visibility",p?"inherit":"hidden",d?"inherit":"hidden",!d)),g!=="scale"&&g!=="transform"&&(g=Kn[g],~g.indexOf(",")&&(g=g.split(",")[0]))),x=g in wi,x){if(this.styles.save(g),f==="string"&&u.substring(0,6)==="var(--"&&(u=Dn(e,u.substring(4,u.indexOf(")"))),d=parseFloat(u)),w||(S=e._gsap,S.renderTransform&&!t.parseTransform||oo(e,t.parseTransform),C=t.smoothOrigin!==!1&&S.smooth,w=this._pt=new sn(this._pt,a,mt,0,1,S.renderTransform,S,0,-1),w.dep=1),g==="scale")this._pt=new sn(this._pt,S,"scaleY",S.scaleY,(v?Qr(S.scaleY,v+d):d)-S.scaleY||0,hu),this._pt.u=0,o.push("scaleY",g),g+="X";else if(g==="transformOrigin"){A.push(on,0,a[on]),u=VA(u),S.svg?mu(e,u,0,C,0,this):(h=parseFloat(u.split(" ")[2])||0,h!==S.zOrigin&&Oi(this,S,"zOrigin",S.zOrigin,h),Oi(this,a,g,Ra(c),Ra(u)));continue}else if(g==="svgOrigin"){mu(e,u,1,C,0,this);continue}else if(g in hg){XA(this,S,g,p,v?Qr(p,v+u):u);continue}else if(g==="smoothOrigin"){Oi(this,S,"smooth",S.smooth,u);continue}else if(g==="force3D"){S[g]=u;continue}else if(g==="transform"){$A(this,u,e);continue}}else g in a||(g=ms(g)||g);if(x||(d||d===0)&&(p||p===0)&&!AA.test(u)&&g in a)m=(c+"").substr((p+"").length),d||(d=0),h=zt(u)||(g in gn.units?gn.units[g]:m),m!==h&&(p=Wi(e,g,c,h)),this._pt=new sn(this._pt,x?S:a,g,p,(v?Qr(p,v+d):d)-p,!x&&(h==="px"||g==="zIndex")&&t.autoRound!==!1?RA:hu),this._pt.u=h||0,m!==h&&h!=="%"&&(this._pt.b=c,this._pt.r=PA);else if(g in a)zA.call(this,e,g,c,v?v+u:u);else if(g in e)this.add(e,g,c||e[g],v?v+u:u,r,s);else if(g!=="parseTransform"){sd(g,u);continue}x||(g in a?A.push(g,0,a[g]):typeof e[g]=="function"?A.push(g,2,e[g]()):A.push(g,1,c||e[g])),o.push(g)}}T&&ig(this)},render:function(e,t){if(t.tween._time||!gd())for(var i=t._pt;i;)i.r(e,i.d),i=i._next;else t.styles.revert()},get:di,aliases:Kn,getSetter:function(e,t,i){var r=Kn[t];return r&&r.indexOf(",")<0&&(t=r),t in wi&&t!==on&&(e._gsap.x||di(e,"x"))?i&&of===i?t==="scale"?UA:IA:(of=i||{})&&(t==="scale"?OA:FA):e.style&&!nd(e.style[t])?DA:~t.indexOf("-")?LA:fd(e,t)},core:{_removeProperty:wr,_getMatrix:vd}};an.utils.checkPrefix=ms;an.core.getStyleSaver=lg;(function(n,e,t,i){var r=rn(n+","+e+","+t,function(s){wi[s]=1});rn(e,function(s){gn.units[s]="deg",hg[s]=1}),Kn[r[13]]=n+","+e,rn(i,function(s){var o=s.split(":");Kn[o[1]]=r[o[0]]})})("x,y,z,scale,scaleX,scaleY,xPercent,yPercent","rotation,rotationX,rotationY,skewX,skewY","transform,transformOrigin,svgOrigin,force3D,smoothOrigin,transformPerspective","0:translateX,1:translateY,2:translateZ,8:rotate,8:rotationZ,8:rotateZ,9:rotateX,10:rotateY");rn("x,y,z,top,right,bottom,left,width,height,fontSize,padding,margin,perspective",function(n){gn.units[n]="px"});an.registerPlugin(mg);var gg=an.registerPlugin(mg)||an;gg.core.Tween;class $a extends jn{constructor(){const e=$a.SkyShader,t=new ti({name:e.name,uniforms:sm.clone(e.uniforms),vertexShader:e.vertexShader,fragmentShader:e.fragmentShader,side:qt,depthWrite:!1});super(new Ss(1,1,1),t),this.isSky=!0}}$a.SkyShader={name:"SkyShader",uniforms:{turbidity:{value:2},rayleigh:{value:1},mieCoefficient:{value:.005},mieDirectionalG:{value:.8},sunPosition:{value:new B},up:{value:new B(0,1,0)}},vertexShader:`
		uniform vec3 sunPosition;
		uniform float rayleigh;
		uniform float turbidity;
		uniform float mieCoefficient;
		uniform vec3 up;

		varying vec3 vWorldPosition;
		varying vec3 vSunDirection;
		varying float vSunfade;
		varying vec3 vBetaR;
		varying vec3 vBetaM;
		varying float vSunE;

		// constants for atmospheric scattering
		const float e = 2.71828182845904523536028747135266249775724709369995957;
		const float pi = 3.141592653589793238462643383279502884197169;

		// wavelength of used primaries, according to preetham
		const vec3 lambda = vec3( 680E-9, 550E-9, 450E-9 );
		// this pre-calculation replaces older TotalRayleigh(vec3 lambda) function:
		// (8.0 * pow(pi, 3.0) * pow(pow(n, 2.0) - 1.0, 2.0) * (6.0 + 3.0 * pn)) / (3.0 * N * pow(lambda, vec3(4.0)) * (6.0 - 7.0 * pn))
		const vec3 totalRayleigh = vec3( 5.804542996261093E-6, 1.3562911419845635E-5, 3.0265902468824876E-5 );

		// mie stuff
		// K coefficient for the primaries
		const float v = 4.0;
		const vec3 K = vec3( 0.686, 0.678, 0.666 );
		// MieConst = pi * pow( ( 2.0 * pi ) / lambda, vec3( v - 2.0 ) ) * K
		const vec3 MieConst = vec3( 1.8399918514433978E14, 2.7798023919660528E14, 4.0790479543861094E14 );

		// earth shadow hack
		// cutoffAngle = pi / 1.95;
		const float cutoffAngle = 1.6110731556870734;
		const float steepness = 1.5;
		const float EE = 1000.0;

		float sunIntensity( float zenithAngleCos ) {
			zenithAngleCos = clamp( zenithAngleCos, -1.0, 1.0 );
			return EE * max( 0.0, 1.0 - pow( e, -( ( cutoffAngle - acos( zenithAngleCos ) ) / steepness ) ) );
		}

		vec3 totalMie( float T ) {
			float c = ( 0.2 * T ) * 10E-18;
			return 0.434 * c * MieConst;
		}

		void main() {

			vec4 worldPosition = modelMatrix * vec4( position, 1.0 );
			vWorldPosition = worldPosition.xyz;

			gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
			gl_Position.z = gl_Position.w; // set z to camera.far

			vSunDirection = normalize( sunPosition );

			vSunE = sunIntensity( dot( vSunDirection, up ) );

			vSunfade = 1.0 - clamp( 1.0 - exp( ( sunPosition.y / 450000.0 ) ), 0.0, 1.0 );

			float rayleighCoefficient = rayleigh - ( 1.0 * ( 1.0 - vSunfade ) );

			// extinction (absorption + out scattering)
			// rayleigh coefficients
			vBetaR = totalRayleigh * rayleighCoefficient;

			// mie coefficients
			vBetaM = totalMie( turbidity ) * mieCoefficient;

		}`,fragmentShader:`
		varying vec3 vWorldPosition;
		varying vec3 vSunDirection;
		varying float vSunfade;
		varying vec3 vBetaR;
		varying vec3 vBetaM;
		varying float vSunE;

		uniform float mieDirectionalG;
		uniform vec3 up;

		// constants for atmospheric scattering
		const float pi = 3.141592653589793238462643383279502884197169;

		const float n = 1.0003; // refractive index of air
		const float N = 2.545E25; // number of molecules per unit volume for air at 288.15K and 1013mb (sea level -45 celsius)

		// optical length at zenith for molecules
		const float rayleighZenithLength = 8.4E3;
		const float mieZenithLength = 1.25E3;
		// 66 arc seconds -> degrees, and the cosine of that
		const float sunAngularDiameterCos = 0.999956676946448443553574619906976478926848692873900859324;

		// 3.0 / ( 16.0 * pi )
		const float THREE_OVER_SIXTEENPI = 0.05968310365946075;
		// 1.0 / ( 4.0 * pi )
		const float ONE_OVER_FOURPI = 0.07957747154594767;

		float rayleighPhase( float cosTheta ) {
			return THREE_OVER_SIXTEENPI * ( 1.0 + pow( cosTheta, 2.0 ) );
		}

		float hgPhase( float cosTheta, float g ) {
			float g2 = pow( g, 2.0 );
			float inverse = 1.0 / pow( 1.0 - 2.0 * g * cosTheta + g2, 1.5 );
			return ONE_OVER_FOURPI * ( ( 1.0 - g2 ) * inverse );
		}

		void main() {

			vec3 direction = normalize( vWorldPosition - cameraPosition );

			// optical length
			// cutoff angle at 90 to avoid singularity in next formula.
			float zenithAngle = acos( max( 0.0, dot( up, direction ) ) );
			float inverse = 1.0 / ( cos( zenithAngle ) + 0.15 * pow( 93.885 - ( ( zenithAngle * 180.0 ) / pi ), -1.253 ) );
			float sR = rayleighZenithLength * inverse;
			float sM = mieZenithLength * inverse;

			// combined extinction factor
			vec3 Fex = exp( -( vBetaR * sR + vBetaM * sM ) );

			// in scattering
			float cosTheta = dot( direction, vSunDirection );

			float rPhase = rayleighPhase( cosTheta * 0.5 + 0.5 );
			vec3 betaRTheta = vBetaR * rPhase;

			float mPhase = hgPhase( cosTheta, mieDirectionalG );
			vec3 betaMTheta = vBetaM * mPhase;

			vec3 Lin = pow( vSunE * ( ( betaRTheta + betaMTheta ) / ( vBetaR + vBetaM ) ) * ( 1.0 - Fex ), vec3( 1.5 ) );
			Lin *= mix( vec3( 1.0 ), pow( vSunE * ( ( betaRTheta + betaMTheta ) / ( vBetaR + vBetaM ) ) * Fex, vec3( 1.0 / 2.0 ) ), clamp( pow( 1.0 - dot( up, vSunDirection ), 5.0 ), 0.0, 1.0 ) );

			// nightsky
			float theta = acos( direction.y ); // elevation --> y-axis, [-pi/2, pi/2]
			float phi = atan( direction.z, direction.x ); // azimuth --> x-axis [-pi/2, pi/2]
			vec2 uv = vec2( phi, theta ) / vec2( 2.0 * pi, pi ) + vec2( 0.5, 0.0 );
			vec3 L0 = vec3( 0.1 ) * Fex;

			// composition + solar disc
			float sundisk = smoothstep( sunAngularDiameterCos, sunAngularDiameterCos + 0.00002, cosTheta );
			L0 += ( vSunE * 19000.0 * Fex ) * sundisk;

			vec3 texColor = ( Lin + L0 ) * 0.04 + vec3( 0.0, 0.0003, 0.00075 );

			vec3 retColor = pow( texColor, vec3( 1.0 / ( 1.2 + ( 1.2 * vSunfade ) ) ) );

			gl_FragColor = vec4( retColor, 1.0 );

			#include <tonemapping_fragment>
			#include <colorspace_fragment>

		}`};const qA=()=>{const n=new ed({width:300,title:"背景調整"});n.name,n.close();const e=document.querySelector("canvas.firework_gl"),t=new ab,i=new vb,r=document.querySelector(".navbar"),s=document.querySelector("footer"),o={width:window.innerWidth,height:window.innerHeight-(r.offsetHeight+s.offsetHeight),pixelRatio:Math.min(window.devicePixelRatio,2)};o.resolution=new Be(o.width*o.pixelRatio,o.height*o.pixelRatio),window.addEventListener("resize",()=>{o.width=window.innerWidth,o.height=window.innerHeight-(r.offsetHeight+s.offsetHeight),o.pixelRatio=Math.min(window.devicePixelRatio,2),o.resolution.set(o.width*o.pixelRatio,o.height*o.pixelRatio),console.log(o.resolution),a.aspect=o.width/o.height,a.updateProjectionMatrix(),c.setSize(o.width,o.height),c.setPixelRatio(o.pixelRatio)});const a=new Cn(25,o.width/o.height,.1,100);a.position.set(1.5,0,6),t.add(a);const l=new o1(a,e);l.enableDamping=!0;const c=new r1({canvas:e,antialias:!0});c.setSize(o.width,o.height),c.setPixelRatio(o.pixelRatio);const u=[i.load("/media/three/firework/1.png"),i.load("/media/three/firework/2.png"),i.load("/media/three/firework/3.png"),i.load("/media/three/firework/4.png"),i.load("/media/three/firework/5.png"),i.load("/media/three/firework/6.png"),i.load("/media/three/firework/7.png"),i.load("/media/three/firework/8.png")],d=(v,x,w,S,C,T)=>{const A=new Float32Array(v*3),b=new Float32Array(v),y=new Float32Array(v);for(let k=0;k<v;k++){const G=k*3,$=new Jc(C*(.75+Math.random()*.25),Math.random()*Math.PI,Math.random()*Math.PI*2),U=new B;U.setFromSpherical($),A[G+0]=U.x,A[G+1]=U.y,A[G+2]=U.z,b[k]=Math.random(),y[k]=1+Math.random()}const P=new yi;P.setAttribute("position",new Jn(A,3)),P.setAttribute("aSize",new Jn(b,1)),P.setAttribute("aTimeMultiplier",new Jn(y,1)),S.flipY=!1;const D=new ti({vertexShader:D1,fragmentShader:L1,uniforms:{uSize:new or(w),uResolution:new or(o.resolution),uTexture:new or(S),uColor:new or(T),uProgress:new or(0)},transparent:!0,depthWrite:!1,blending:lc}),O=new hb(P,D);O.position.copy(x),t.add(O);const V=()=>{t.remove(O),P.dispose(),D.dispose()};gg.to(D.uniforms.uProgress,{value:1,duration:5,ease:"linear",onComplete:V})},p=()=>{const v=Math.round(400+Math.random()*1e3),x=new B((Math.random()-.5)*2,Math.random(),(Math.random()-.5)*2),w=.1+Math.random()*.1,S=u[Math.floor(Math.random()*u.length)],C=.5+Math.random(),T=new Ze;T.setHSL(Math.random(),1,.7),d(v,x,w,S,C,T)};p(),window.addEventListener("click",()=>{p()});const f=new $a;f.scale.setScalar(45e4),t.add(f);const _=new B,g={turbidity:10,rayleigh:3,mieCoefficient:.005,mieDirectionalG:.95,elevation:-2.2,azimuth:180,exposure:c.toneMappingExposure},m=()=>{const v=f.material.uniforms;v.turbidity.value=g.turbidity,v.rayleigh.value=g.rayleigh,v.mieCoefficient.value=g.mieCoefficient,v.mieDirectionalG.value=g.mieDirectionalG;const x=Kc.degToRad(90-g.elevation),w=Kc.degToRad(g.azimuth);_.setFromSphericalCoords(1,x,w),v.sunPosition.value.copy(_),c.toneMappingExposure=g.exposure,c.render(t,a)};n.add(g,"turbidity").min(0).max(20).step(.1).onChange(m),n.add(g,"rayleigh").min(0).max(4).step(.001).onChange(m),n.add(g,"mieCoefficient").min(0).max(.1).step(.001).onChange(m),n.add(g,"mieDirectionalG").min(0).max(1).step(.001).onChange(m),n.add(g,"elevation").min(-3).max(10).step(.1).onChange(m),n.add(g,"azimuth").min(-180).max(180).step(.1).onChange(m),n.add(g,"exposure").min(0).max(1).step(1e-4).onChange(m),m();const h=()=>{l.update(),c.render(t,a),window.requestAnimationFrame(h)};h()};window.addEventListener("scroll",function(){const n=document.querySelector("#navbar");window.scrollY>100?n.classList.add("scrolled-background"):n.classList.remove("scrolled-background")});new Tn(".swiper",{modules:[G_,W_],direction:"horizontal",loop:!0,pagination:{el:".swiper-pagination"},navigation:{nextEl:".swiper-btn-next",prevEl:".swiper-btn-prev"},scrollbar:{el:".swiper-scrollbar"}});const YA=(n,e)=>{var t=new Date(n),i=new Date(e);return(i-t)/(1e3*3600*24)},jA=(n,e)=>{document.getElementById("cally1").innerText,document.getElementById("cally2").innerText;const t=document.getElementById("callyDate1"),i=document.getElementById("callyDate2");document.getElementById(e).innerText=n.value,e==="cally1"?i.setAttribute("min",n.value):e==="cally2"&&t.setAttribute("max",n.value)},KA=()=>{document.getElementById("cally1").innerText="開始日期",document.getElementById("cally2").innerText="截止日期";const n=document.getElementById("callyDate1"),e=document.getElementById("callyDate2");n.removeAttribute("max"),e.removeAttribute("min")},ZA=()=>{const n=document.getElementById("cally1").innerText,e=document.getElementById("cally2").innerText;n!="開始日期"&&e!="截止日期"?console.log("ready"):Xs.fire({title:"【開始】與【截止】日期都要選喔！",text:"單日的話請都選同一天",icon:"error"})};window.onload=function(){document.querySelector(".webgl"),document.querySelector(".firework_gl")&&(qA(),Xs.fire({title:"點擊場景點燃🎆",text:"🖱️左鍵拖拽可觀看3D景色",icon:"info"}))};window.daysBetween=YA;window.datePicker=jA;window.searchArchive=ZA;window.resetDate=KA;
