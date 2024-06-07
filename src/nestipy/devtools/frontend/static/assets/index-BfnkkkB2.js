(function(){const n=document.createElement("link").relList;if(n&&n.supports&&n.supports("modulepreload"))return;for(const o of document.querySelectorAll('link[rel="modulepreload"]'))r(o);new MutationObserver(o=>{for(const i of o)if(i.type==="childList")for(const a of i.addedNodes)a.tagName==="LINK"&&a.rel==="modulepreload"&&r(a)}).observe(document,{childList:!0,subtree:!0});function t(o){const i={};return o.integrity&&(i.integrity=o.integrity),o.referrerPolicy&&(i.referrerPolicy=o.referrerPolicy),o.crossOrigin==="use-credentials"?i.credentials="include":o.crossOrigin==="anonymous"?i.credentials="omit":i.credentials="same-origin",i}function r(o){if(o.ep)return;o.ep=!0;const i=t(o);fetch(o.href,i)}})();function Mc(e){return e&&e.__esModule&&Object.prototype.hasOwnProperty.call(e,"default")?e.default:e}var cl={exports:{}},mo={},pl={exports:{}},F={};/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var ar=Symbol.for("react.element"),Lc=Symbol.for("react.portal"),jc=Symbol.for("react.fragment"),Dc=Symbol.for("react.strict_mode"),zc=Symbol.for("react.profiler"),Uc=Symbol.for("react.provider"),Bc=Symbol.for("react.context"),$c=Symbol.for("react.forward_ref"),Hc=Symbol.for("react.suspense"),qc=Symbol.for("react.memo"),Vc=Symbol.for("react.lazy"),Ka=Symbol.iterator;function Gc(e){return e===null||typeof e!="object"?null:(e=Ka&&e[Ka]||e["@@iterator"],typeof e=="function"?e:null)}var dl={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},fl=Object.assign,ml={};function vt(e,n,t){this.props=e,this.context=n,this.refs=ml,this.updater=t||dl}vt.prototype.isReactComponent={};vt.prototype.setState=function(e,n){if(typeof e!="object"&&typeof e!="function"&&e!=null)throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,e,n,"setState")};vt.prototype.forceUpdate=function(e){this.updater.enqueueForceUpdate(this,e,"forceUpdate")};function yl(){}yl.prototype=vt.prototype;function Xi(e,n,t){this.props=e,this.context=n,this.refs=ml,this.updater=t||dl}var Ji=Xi.prototype=new yl;Ji.constructor=Xi;fl(Ji,vt.prototype);Ji.isPureReactComponent=!0;var Ya=Array.isArray,gl=Object.prototype.hasOwnProperty,ea={current:null},_l={key:!0,ref:!0,__self:!0,__source:!0};function hl(e,n,t){var r,o={},i=null,a=null;if(n!=null)for(r in n.ref!==void 0&&(a=n.ref),n.key!==void 0&&(i=""+n.key),n)gl.call(n,r)&&!_l.hasOwnProperty(r)&&(o[r]=n[r]);var s=arguments.length-2;if(s===1)o.children=t;else if(1<s){for(var l=Array(s),p=0;p<s;p++)l[p]=arguments[p+2];o.children=l}if(e&&e.defaultProps)for(r in s=e.defaultProps,s)o[r]===void 0&&(o[r]=s[r]);return{$$typeof:ar,type:e,key:i,ref:a,props:o,_owner:ea.current}}function Wc(e,n){return{$$typeof:ar,type:e.type,key:n,ref:e.ref,props:e.props,_owner:e._owner}}function na(e){return typeof e=="object"&&e!==null&&e.$$typeof===ar}function Kc(e){var n={"=":"=0",":":"=2"};return"$"+e.replace(/[=:]/g,function(t){return n[t]})}var Qa=/\/+/g;function Fo(e,n){return typeof e=="object"&&e!==null&&e.key!=null?Kc(""+e.key):n.toString(36)}function Rr(e,n,t,r,o){var i=typeof e;(i==="undefined"||i==="boolean")&&(e=null);var a=!1;if(e===null)a=!0;else switch(i){case"string":case"number":a=!0;break;case"object":switch(e.$$typeof){case ar:case Lc:a=!0}}if(a)return a=e,o=o(a),e=r===""?"."+Fo(a,0):r,Ya(o)?(t="",e!=null&&(t=e.replace(Qa,"$&/")+"/"),Rr(o,n,t,"",function(p){return p})):o!=null&&(na(o)&&(o=Wc(o,t+(!o.key||a&&a.key===o.key?"":(""+o.key).replace(Qa,"$&/")+"/")+e)),n.push(o)),1;if(a=0,r=r===""?".":r+":",Ya(e))for(var s=0;s<e.length;s++){i=e[s];var l=r+Fo(i,s);a+=Rr(i,n,t,l,o)}else if(l=Gc(e),typeof l=="function")for(e=l.call(e),s=0;!(i=e.next()).done;)i=i.value,l=r+Fo(i,s++),a+=Rr(i,n,t,l,o);else if(i==="object")throw n=String(e),Error("Objects are not valid as a React child (found: "+(n==="[object Object]"?"object with keys {"+Object.keys(e).join(", ")+"}":n)+"). If you meant to render a collection of children, use an array instead.");return a}function pr(e,n,t){if(e==null)return e;var r=[],o=0;return Rr(e,r,"","",function(i){return n.call(t,i,o++)}),r}function Yc(e){if(e._status===-1){var n=e._result;n=n(),n.then(function(t){(e._status===0||e._status===-1)&&(e._status=1,e._result=t)},function(t){(e._status===0||e._status===-1)&&(e._status=2,e._result=t)}),e._status===-1&&(e._status=0,e._result=n)}if(e._status===1)return e._result.default;throw e._result}var de={current:null},Tr={transition:null},Qc={ReactCurrentDispatcher:de,ReactCurrentBatchConfig:Tr,ReactCurrentOwner:ea};function vl(){throw Error("act(...) is not supported in production builds of React.")}F.Children={map:pr,forEach:function(e,n,t){pr(e,function(){n.apply(this,arguments)},t)},count:function(e){var n=0;return pr(e,function(){n++}),n},toArray:function(e){return pr(e,function(n){return n})||[]},only:function(e){if(!na(e))throw Error("React.Children.only expected to receive a single React element child.");return e}};F.Component=vt;F.Fragment=jc;F.Profiler=zc;F.PureComponent=Xi;F.StrictMode=Dc;F.Suspense=Hc;F.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=Qc;F.act=vl;F.cloneElement=function(e,n,t){if(e==null)throw Error("React.cloneElement(...): The argument must be a React element, but you passed "+e+".");var r=fl({},e.props),o=e.key,i=e.ref,a=e._owner;if(n!=null){if(n.ref!==void 0&&(i=n.ref,a=ea.current),n.key!==void 0&&(o=""+n.key),e.type&&e.type.defaultProps)var s=e.type.defaultProps;for(l in n)gl.call(n,l)&&!_l.hasOwnProperty(l)&&(r[l]=n[l]===void 0&&s!==void 0?s[l]:n[l])}var l=arguments.length-2;if(l===1)r.children=t;else if(1<l){s=Array(l);for(var p=0;p<l;p++)s[p]=arguments[p+2];r.children=s}return{$$typeof:ar,type:e.type,key:o,ref:i,props:r,_owner:a}};F.createContext=function(e){return e={$$typeof:Bc,_currentValue:e,_currentValue2:e,_threadCount:0,Provider:null,Consumer:null,_defaultValue:null,_globalName:null},e.Provider={$$typeof:Uc,_context:e},e.Consumer=e};F.createElement=hl;F.createFactory=function(e){var n=hl.bind(null,e);return n.type=e,n};F.createRef=function(){return{current:null}};F.forwardRef=function(e){return{$$typeof:$c,render:e}};F.isValidElement=na;F.lazy=function(e){return{$$typeof:Vc,_payload:{_status:-1,_result:e},_init:Yc}};F.memo=function(e,n){return{$$typeof:qc,type:e,compare:n===void 0?null:n}};F.startTransition=function(e){var n=Tr.transition;Tr.transition={};try{e()}finally{Tr.transition=n}};F.unstable_act=vl;F.useCallback=function(e,n){return de.current.useCallback(e,n)};F.useContext=function(e){return de.current.useContext(e)};F.useDebugValue=function(){};F.useDeferredValue=function(e){return de.current.useDeferredValue(e)};F.useEffect=function(e,n){return de.current.useEffect(e,n)};F.useId=function(){return de.current.useId()};F.useImperativeHandle=function(e,n,t){return de.current.useImperativeHandle(e,n,t)};F.useInsertionEffect=function(e,n){return de.current.useInsertionEffect(e,n)};F.useLayoutEffect=function(e,n){return de.current.useLayoutEffect(e,n)};F.useMemo=function(e,n){return de.current.useMemo(e,n)};F.useReducer=function(e,n,t){return de.current.useReducer(e,n,t)};F.useRef=function(e){return de.current.useRef(e)};F.useState=function(e){return de.current.useState(e)};F.useSyncExternalStore=function(e,n,t){return de.current.useSyncExternalStore(e,n,t)};F.useTransition=function(){return de.current.useTransition()};F.version="18.3.1";pl.exports=F;var z=pl.exports;const ze=Mc(z);/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var Zc=z,Xc=Symbol.for("react.element"),Jc=Symbol.for("react.fragment"),ep=Object.prototype.hasOwnProperty,np=Zc.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,tp={key:!0,ref:!0,__self:!0,__source:!0};function xl(e,n,t){var r,o={},i=null,a=null;t!==void 0&&(i=""+t),n.key!==void 0&&(i=""+n.key),n.ref!==void 0&&(a=n.ref);for(r in n)ep.call(n,r)&&!tp.hasOwnProperty(r)&&(o[r]=n[r]);if(e&&e.defaultProps)for(r in n=e.defaultProps,n)o[r]===void 0&&(o[r]=n[r]);return{$$typeof:Xc,type:e,key:i,ref:a,props:o,_owner:np.current}}mo.Fragment=Jc;mo.jsx=xl;mo.jsxs=xl;cl.exports=mo;var I=cl.exports,ii={},wl={exports:{}},Se={},kl={exports:{}},El={};/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */(function(e){function n(b,P){var T=b.length;b.push(P);e:for(;0<T;){var j=T-1>>>1,H=b[j];if(0<o(H,P))b[j]=P,b[T]=H,T=j;else break e}}function t(b){return b.length===0?null:b[0]}function r(b){if(b.length===0)return null;var P=b[0],T=b.pop();if(T!==P){b[0]=T;e:for(var j=0,H=b.length,Qe=H>>>1;j<Qe;){var Fe=2*(j+1)-1,Gn=b[Fe],Oe=Fe+1,Ze=b[Oe];if(0>o(Gn,T))Oe<H&&0>o(Ze,Gn)?(b[j]=Ze,b[Oe]=T,j=Oe):(b[j]=Gn,b[Fe]=T,j=Fe);else if(Oe<H&&0>o(Ze,T))b[j]=Ze,b[Oe]=T,j=Oe;else break e}}return P}function o(b,P){var T=b.sortIndex-P.sortIndex;return T!==0?T:b.id-P.id}if(typeof performance=="object"&&typeof performance.now=="function"){var i=performance;e.unstable_now=function(){return i.now()}}else{var a=Date,s=a.now();e.unstable_now=function(){return a.now()-s}}var l=[],p=[],g=1,y=null,_=3,w=!1,f=!1,m=!1,h=typeof setTimeout=="function"?setTimeout:null,c=typeof clearTimeout=="function"?clearTimeout:null,u=typeof setImmediate<"u"?setImmediate:null;typeof navigator<"u"&&navigator.scheduling!==void 0&&navigator.scheduling.isInputPending!==void 0&&navigator.scheduling.isInputPending.bind(navigator.scheduling);function d(b){for(var P=t(p);P!==null;){if(P.callback===null)r(p);else if(P.startTime<=b)r(p),P.sortIndex=P.expirationTime,n(l,P);else break;P=t(p)}}function v(b){if(m=!1,d(b),!f)if(t(l)!==null)f=!0,He(k);else{var P=t(p);P!==null&&cn(v,P.startTime-b)}}function k(b,P){f=!1,m&&(m=!1,c(N),N=-1),w=!0;var T=_;try{for(d(P),y=t(l);y!==null&&(!(y.expirationTime>P)||b&&!K());){var j=y.callback;if(typeof j=="function"){y.callback=null,_=y.priorityLevel;var H=j(y.expirationTime<=P);P=e.unstable_now(),typeof H=="function"?y.callback=H:y===t(l)&&r(l),d(P)}else r(l);y=t(l)}if(y!==null)var Qe=!0;else{var Fe=t(p);Fe!==null&&cn(v,Fe.startTime-P),Qe=!1}return Qe}finally{y=null,_=T,w=!1}}var C=!1,S=null,N=-1,O=5,A=-1;function K(){return!(e.unstable_now()-A<O)}function ie(){if(S!==null){var b=e.unstable_now();A=b;var P=!0;try{P=S(!0,b)}finally{P?un():(C=!1,S=null)}}else C=!1}var un;if(typeof u=="function")un=function(){u(ie)};else if(typeof MessageChannel<"u"){var Z=new MessageChannel,Ce=Z.port2;Z.port1.onmessage=ie,un=function(){Ce.postMessage(null)}}else un=function(){h(ie,0)};function He(b){S=b,C||(C=!0,un())}function cn(b,P){N=h(function(){b(e.unstable_now())},P)}e.unstable_IdlePriority=5,e.unstable_ImmediatePriority=1,e.unstable_LowPriority=4,e.unstable_NormalPriority=3,e.unstable_Profiling=null,e.unstable_UserBlockingPriority=2,e.unstable_cancelCallback=function(b){b.callback=null},e.unstable_continueExecution=function(){f||w||(f=!0,He(k))},e.unstable_forceFrameRate=function(b){0>b||125<b?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):O=0<b?Math.floor(1e3/b):5},e.unstable_getCurrentPriorityLevel=function(){return _},e.unstable_getFirstCallbackNode=function(){return t(l)},e.unstable_next=function(b){switch(_){case 1:case 2:case 3:var P=3;break;default:P=_}var T=_;_=P;try{return b()}finally{_=T}},e.unstable_pauseExecution=function(){},e.unstable_requestPaint=function(){},e.unstable_runWithPriority=function(b,P){switch(b){case 1:case 2:case 3:case 4:case 5:break;default:b=3}var T=_;_=b;try{return P()}finally{_=T}},e.unstable_scheduleCallback=function(b,P,T){var j=e.unstable_now();switch(typeof T=="object"&&T!==null?(T=T.delay,T=typeof T=="number"&&0<T?j+T:j):T=j,b){case 1:var H=-1;break;case 2:H=250;break;case 5:H=1073741823;break;case 4:H=1e4;break;default:H=5e3}return H=T+H,b={id:g++,callback:P,priorityLevel:b,startTime:T,expirationTime:H,sortIndex:-1},T>j?(b.sortIndex=T,n(p,b),t(l)===null&&b===t(p)&&(m?(c(N),N=-1):m=!0,cn(v,T-j))):(b.sortIndex=H,n(l,b),f||w||(f=!0,He(k))),b},e.unstable_shouldYield=K,e.unstable_wrapCallback=function(b){var P=_;return function(){var T=_;_=P;try{return b.apply(this,arguments)}finally{_=T}}}})(El);kl.exports=El;var rp=kl.exports;/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var op=z,Ee=rp;function E(e){for(var n="https://reactjs.org/docs/error-decoder.html?invariant="+e,t=1;t<arguments.length;t++)n+="&args[]="+encodeURIComponent(arguments[t]);return"Minified React error #"+e+"; visit "+n+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}var Sl=new Set,Ht={};function qn(e,n){dt(e,n),dt(e+"Capture",n)}function dt(e,n){for(Ht[e]=n,e=0;e<n.length;e++)Sl.add(n[e])}var rn=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),ai=Object.prototype.hasOwnProperty,ip=/^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,Za={},Xa={};function ap(e){return ai.call(Xa,e)?!0:ai.call(Za,e)?!1:ip.test(e)?Xa[e]=!0:(Za[e]=!0,!1)}function sp(e,n,t,r){if(t!==null&&t.type===0)return!1;switch(typeof n){case"function":case"symbol":return!0;case"boolean":return r?!1:t!==null?!t.acceptsBooleans:(e=e.toLowerCase().slice(0,5),e!=="data-"&&e!=="aria-");default:return!1}}function lp(e,n,t,r){if(n===null||typeof n>"u"||sp(e,n,t,r))return!0;if(r)return!1;if(t!==null)switch(t.type){case 3:return!n;case 4:return n===!1;case 5:return isNaN(n);case 6:return isNaN(n)||1>n}return!1}function fe(e,n,t,r,o,i,a){this.acceptsBooleans=n===2||n===3||n===4,this.attributeName=r,this.attributeNamespace=o,this.mustUseProperty=t,this.propertyName=e,this.type=n,this.sanitizeURL=i,this.removeEmptyString=a}var oe={};"children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style".split(" ").forEach(function(e){oe[e]=new fe(e,0,!1,e,null,!1,!1)});[["acceptCharset","accept-charset"],["className","class"],["htmlFor","for"],["httpEquiv","http-equiv"]].forEach(function(e){var n=e[0];oe[n]=new fe(n,1,!1,e[1],null,!1,!1)});["contentEditable","draggable","spellCheck","value"].forEach(function(e){oe[e]=new fe(e,2,!1,e.toLowerCase(),null,!1,!1)});["autoReverse","externalResourcesRequired","focusable","preserveAlpha"].forEach(function(e){oe[e]=new fe(e,2,!1,e,null,!1,!1)});"allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope".split(" ").forEach(function(e){oe[e]=new fe(e,3,!1,e.toLowerCase(),null,!1,!1)});["checked","multiple","muted","selected"].forEach(function(e){oe[e]=new fe(e,3,!0,e,null,!1,!1)});["capture","download"].forEach(function(e){oe[e]=new fe(e,4,!1,e,null,!1,!1)});["cols","rows","size","span"].forEach(function(e){oe[e]=new fe(e,6,!1,e,null,!1,!1)});["rowSpan","start"].forEach(function(e){oe[e]=new fe(e,5,!1,e.toLowerCase(),null,!1,!1)});var ta=/[\-:]([a-z])/g;function ra(e){return e[1].toUpperCase()}"accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height".split(" ").forEach(function(e){var n=e.replace(ta,ra);oe[n]=new fe(n,1,!1,e,null,!1,!1)});"xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type".split(" ").forEach(function(e){var n=e.replace(ta,ra);oe[n]=new fe(n,1,!1,e,"http://www.w3.org/1999/xlink",!1,!1)});["xml:base","xml:lang","xml:space"].forEach(function(e){var n=e.replace(ta,ra);oe[n]=new fe(n,1,!1,e,"http://www.w3.org/XML/1998/namespace",!1,!1)});["tabIndex","crossOrigin"].forEach(function(e){oe[e]=new fe(e,1,!1,e.toLowerCase(),null,!1,!1)});oe.xlinkHref=new fe("xlinkHref",1,!1,"xlink:href","http://www.w3.org/1999/xlink",!0,!1);["src","href","action","formAction"].forEach(function(e){oe[e]=new fe(e,1,!1,e.toLowerCase(),null,!0,!0)});function oa(e,n,t,r){var o=oe.hasOwnProperty(n)?oe[n]:null;(o!==null?o.type!==0:r||!(2<n.length)||n[0]!=="o"&&n[0]!=="O"||n[1]!=="n"&&n[1]!=="N")&&(lp(n,t,o,r)&&(t=null),r||o===null?ap(n)&&(t===null?e.removeAttribute(n):e.setAttribute(n,""+t)):o.mustUseProperty?e[o.propertyName]=t===null?o.type===3?!1:"":t:(n=o.attributeName,r=o.attributeNamespace,t===null?e.removeAttribute(n):(o=o.type,t=o===3||o===4&&t===!0?"":""+t,r?e.setAttributeNS(r,n,t):e.setAttribute(n,t))))}var ln=op.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,dr=Symbol.for("react.element"),Kn=Symbol.for("react.portal"),Yn=Symbol.for("react.fragment"),ia=Symbol.for("react.strict_mode"),si=Symbol.for("react.profiler"),bl=Symbol.for("react.provider"),Cl=Symbol.for("react.context"),aa=Symbol.for("react.forward_ref"),li=Symbol.for("react.suspense"),ui=Symbol.for("react.suspense_list"),sa=Symbol.for("react.memo"),dn=Symbol.for("react.lazy"),Nl=Symbol.for("react.offscreen"),Ja=Symbol.iterator;function kt(e){return e===null||typeof e!="object"?null:(e=Ja&&e[Ja]||e["@@iterator"],typeof e=="function"?e:null)}var G=Object.assign,Oo;function At(e){if(Oo===void 0)try{throw Error()}catch(t){var n=t.stack.trim().match(/\n( *(at )?)/);Oo=n&&n[1]||""}return`
`+Oo+e}var Mo=!1;function Lo(e,n){if(!e||Mo)return"";Mo=!0;var t=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{if(n)if(n=function(){throw Error()},Object.defineProperty(n.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(n,[])}catch(p){var r=p}Reflect.construct(e,[],n)}else{try{n.call()}catch(p){r=p}e.call(n.prototype)}else{try{throw Error()}catch(p){r=p}e()}}catch(p){if(p&&r&&typeof p.stack=="string"){for(var o=p.stack.split(`
`),i=r.stack.split(`
`),a=o.length-1,s=i.length-1;1<=a&&0<=s&&o[a]!==i[s];)s--;for(;1<=a&&0<=s;a--,s--)if(o[a]!==i[s]){if(a!==1||s!==1)do if(a--,s--,0>s||o[a]!==i[s]){var l=`
`+o[a].replace(" at new "," at ");return e.displayName&&l.includes("<anonymous>")&&(l=l.replace("<anonymous>",e.displayName)),l}while(1<=a&&0<=s);break}}}finally{Mo=!1,Error.prepareStackTrace=t}return(e=e?e.displayName||e.name:"")?At(e):""}function up(e){switch(e.tag){case 5:return At(e.type);case 16:return At("Lazy");case 13:return At("Suspense");case 19:return At("SuspenseList");case 0:case 2:case 15:return e=Lo(e.type,!1),e;case 11:return e=Lo(e.type.render,!1),e;case 1:return e=Lo(e.type,!0),e;default:return""}}function ci(e){if(e==null)return null;if(typeof e=="function")return e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case Yn:return"Fragment";case Kn:return"Portal";case si:return"Profiler";case ia:return"StrictMode";case li:return"Suspense";case ui:return"SuspenseList"}if(typeof e=="object")switch(e.$$typeof){case Cl:return(e.displayName||"Context")+".Consumer";case bl:return(e._context.displayName||"Context")+".Provider";case aa:var n=e.render;return e=e.displayName,e||(e=n.displayName||n.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case sa:return n=e.displayName||null,n!==null?n:ci(e.type)||"Memo";case dn:n=e._payload,e=e._init;try{return ci(e(n))}catch{}}return null}function cp(e){var n=e.type;switch(e.tag){case 24:return"Cache";case 9:return(n.displayName||"Context")+".Consumer";case 10:return(n._context.displayName||"Context")+".Provider";case 18:return"DehydratedFragment";case 11:return e=n.render,e=e.displayName||e.name||"",n.displayName||(e!==""?"ForwardRef("+e+")":"ForwardRef");case 7:return"Fragment";case 5:return n;case 4:return"Portal";case 3:return"Root";case 6:return"Text";case 16:return ci(n);case 8:return n===ia?"StrictMode":"Mode";case 22:return"Offscreen";case 12:return"Profiler";case 21:return"Scope";case 13:return"Suspense";case 19:return"SuspenseList";case 25:return"TracingMarker";case 1:case 0:case 17:case 2:case 14:case 15:if(typeof n=="function")return n.displayName||n.name||null;if(typeof n=="string")return n}return null}function Nn(e){switch(typeof e){case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function Rl(e){var n=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(n==="checkbox"||n==="radio")}function pp(e){var n=Rl(e)?"checked":"value",t=Object.getOwnPropertyDescriptor(e.constructor.prototype,n),r=""+e[n];if(!e.hasOwnProperty(n)&&typeof t<"u"&&typeof t.get=="function"&&typeof t.set=="function"){var o=t.get,i=t.set;return Object.defineProperty(e,n,{configurable:!0,get:function(){return o.call(this)},set:function(a){r=""+a,i.call(this,a)}}),Object.defineProperty(e,n,{enumerable:t.enumerable}),{getValue:function(){return r},setValue:function(a){r=""+a},stopTracking:function(){e._valueTracker=null,delete e[n]}}}}function fr(e){e._valueTracker||(e._valueTracker=pp(e))}function Tl(e){if(!e)return!1;var n=e._valueTracker;if(!n)return!0;var t=n.getValue(),r="";return e&&(r=Rl(e)?e.checked?"true":"false":e.value),e=r,e!==t?(n.setValue(e),!0):!1}function Ur(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}function pi(e,n){var t=n.checked;return G({},n,{defaultChecked:void 0,defaultValue:void 0,value:void 0,checked:t??e._wrapperState.initialChecked})}function es(e,n){var t=n.defaultValue==null?"":n.defaultValue,r=n.checked!=null?n.checked:n.defaultChecked;t=Nn(n.value!=null?n.value:t),e._wrapperState={initialChecked:r,initialValue:t,controlled:n.type==="checkbox"||n.type==="radio"?n.checked!=null:n.value!=null}}function Al(e,n){n=n.checked,n!=null&&oa(e,"checked",n,!1)}function di(e,n){Al(e,n);var t=Nn(n.value),r=n.type;if(t!=null)r==="number"?(t===0&&e.value===""||e.value!=t)&&(e.value=""+t):e.value!==""+t&&(e.value=""+t);else if(r==="submit"||r==="reset"){e.removeAttribute("value");return}n.hasOwnProperty("value")?fi(e,n.type,t):n.hasOwnProperty("defaultValue")&&fi(e,n.type,Nn(n.defaultValue)),n.checked==null&&n.defaultChecked!=null&&(e.defaultChecked=!!n.defaultChecked)}function ns(e,n,t){if(n.hasOwnProperty("value")||n.hasOwnProperty("defaultValue")){var r=n.type;if(!(r!=="submit"&&r!=="reset"||n.value!==void 0&&n.value!==null))return;n=""+e._wrapperState.initialValue,t||n===e.value||(e.value=n),e.defaultValue=n}t=e.name,t!==""&&(e.name=""),e.defaultChecked=!!e._wrapperState.initialChecked,t!==""&&(e.name=t)}function fi(e,n,t){(n!=="number"||Ur(e.ownerDocument)!==e)&&(t==null?e.defaultValue=""+e._wrapperState.initialValue:e.defaultValue!==""+t&&(e.defaultValue=""+t))}var Pt=Array.isArray;function at(e,n,t,r){if(e=e.options,n){n={};for(var o=0;o<t.length;o++)n["$"+t[o]]=!0;for(t=0;t<e.length;t++)o=n.hasOwnProperty("$"+e[t].value),e[t].selected!==o&&(e[t].selected=o),o&&r&&(e[t].defaultSelected=!0)}else{for(t=""+Nn(t),n=null,o=0;o<e.length;o++){if(e[o].value===t){e[o].selected=!0,r&&(e[o].defaultSelected=!0);return}n!==null||e[o].disabled||(n=e[o])}n!==null&&(n.selected=!0)}}function mi(e,n){if(n.dangerouslySetInnerHTML!=null)throw Error(E(91));return G({},n,{value:void 0,defaultValue:void 0,children:""+e._wrapperState.initialValue})}function ts(e,n){var t=n.value;if(t==null){if(t=n.children,n=n.defaultValue,t!=null){if(n!=null)throw Error(E(92));if(Pt(t)){if(1<t.length)throw Error(E(93));t=t[0]}n=t}n==null&&(n=""),t=n}e._wrapperState={initialValue:Nn(t)}}function Pl(e,n){var t=Nn(n.value),r=Nn(n.defaultValue);t!=null&&(t=""+t,t!==e.value&&(e.value=t),n.defaultValue==null&&e.defaultValue!==t&&(e.defaultValue=t)),r!=null&&(e.defaultValue=""+r)}function rs(e){var n=e.textContent;n===e._wrapperState.initialValue&&n!==""&&n!==null&&(e.value=n)}function Il(e){switch(e){case"svg":return"http://www.w3.org/2000/svg";case"math":return"http://www.w3.org/1998/Math/MathML";default:return"http://www.w3.org/1999/xhtml"}}function yi(e,n){return e==null||e==="http://www.w3.org/1999/xhtml"?Il(n):e==="http://www.w3.org/2000/svg"&&n==="foreignObject"?"http://www.w3.org/1999/xhtml":e}var mr,Fl=function(e){return typeof MSApp<"u"&&MSApp.execUnsafeLocalFunction?function(n,t,r,o){MSApp.execUnsafeLocalFunction(function(){return e(n,t,r,o)})}:e}(function(e,n){if(e.namespaceURI!=="http://www.w3.org/2000/svg"||"innerHTML"in e)e.innerHTML=n;else{for(mr=mr||document.createElement("div"),mr.innerHTML="<svg>"+n.valueOf().toString()+"</svg>",n=mr.firstChild;e.firstChild;)e.removeChild(e.firstChild);for(;n.firstChild;)e.appendChild(n.firstChild)}});function qt(e,n){if(n){var t=e.firstChild;if(t&&t===e.lastChild&&t.nodeType===3){t.nodeValue=n;return}}e.textContent=n}var Ot={animationIterationCount:!0,aspectRatio:!0,borderImageOutset:!0,borderImageSlice:!0,borderImageWidth:!0,boxFlex:!0,boxFlexGroup:!0,boxOrdinalGroup:!0,columnCount:!0,columns:!0,flex:!0,flexGrow:!0,flexPositive:!0,flexShrink:!0,flexNegative:!0,flexOrder:!0,gridArea:!0,gridRow:!0,gridRowEnd:!0,gridRowSpan:!0,gridRowStart:!0,gridColumn:!0,gridColumnEnd:!0,gridColumnSpan:!0,gridColumnStart:!0,fontWeight:!0,lineClamp:!0,lineHeight:!0,opacity:!0,order:!0,orphans:!0,tabSize:!0,widows:!0,zIndex:!0,zoom:!0,fillOpacity:!0,floodOpacity:!0,stopOpacity:!0,strokeDasharray:!0,strokeDashoffset:!0,strokeMiterlimit:!0,strokeOpacity:!0,strokeWidth:!0},dp=["Webkit","ms","Moz","O"];Object.keys(Ot).forEach(function(e){dp.forEach(function(n){n=n+e.charAt(0).toUpperCase()+e.substring(1),Ot[n]=Ot[e]})});function Ol(e,n,t){return n==null||typeof n=="boolean"||n===""?"":t||typeof n!="number"||n===0||Ot.hasOwnProperty(e)&&Ot[e]?(""+n).trim():n+"px"}function Ml(e,n){e=e.style;for(var t in n)if(n.hasOwnProperty(t)){var r=t.indexOf("--")===0,o=Ol(t,n[t],r);t==="float"&&(t="cssFloat"),r?e.setProperty(t,o):e[t]=o}}var fp=G({menuitem:!0},{area:!0,base:!0,br:!0,col:!0,embed:!0,hr:!0,img:!0,input:!0,keygen:!0,link:!0,meta:!0,param:!0,source:!0,track:!0,wbr:!0});function gi(e,n){if(n){if(fp[e]&&(n.children!=null||n.dangerouslySetInnerHTML!=null))throw Error(E(137,e));if(n.dangerouslySetInnerHTML!=null){if(n.children!=null)throw Error(E(60));if(typeof n.dangerouslySetInnerHTML!="object"||!("__html"in n.dangerouslySetInnerHTML))throw Error(E(61))}if(n.style!=null&&typeof n.style!="object")throw Error(E(62))}}function _i(e,n){if(e.indexOf("-")===-1)return typeof n.is=="string";switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var hi=null;function la(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var vi=null,st=null,lt=null;function os(e){if(e=ur(e)){if(typeof vi!="function")throw Error(E(280));var n=e.stateNode;n&&(n=vo(n),vi(e.stateNode,e.type,n))}}function Ll(e){st?lt?lt.push(e):lt=[e]:st=e}function jl(){if(st){var e=st,n=lt;if(lt=st=null,os(e),n)for(e=0;e<n.length;e++)os(n[e])}}function Dl(e,n){return e(n)}function zl(){}var jo=!1;function Ul(e,n,t){if(jo)return e(n,t);jo=!0;try{return Dl(e,n,t)}finally{jo=!1,(st!==null||lt!==null)&&(zl(),jl())}}function Vt(e,n){var t=e.stateNode;if(t===null)return null;var r=vo(t);if(r===null)return null;t=r[n];e:switch(n){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(r=!r.disabled)||(e=e.type,r=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!r;break e;default:e=!1}if(e)return null;if(t&&typeof t!="function")throw Error(E(231,n,typeof t));return t}var xi=!1;if(rn)try{var Et={};Object.defineProperty(Et,"passive",{get:function(){xi=!0}}),window.addEventListener("test",Et,Et),window.removeEventListener("test",Et,Et)}catch{xi=!1}function mp(e,n,t,r,o,i,a,s,l){var p=Array.prototype.slice.call(arguments,3);try{n.apply(t,p)}catch(g){this.onError(g)}}var Mt=!1,Br=null,$r=!1,wi=null,yp={onError:function(e){Mt=!0,Br=e}};function gp(e,n,t,r,o,i,a,s,l){Mt=!1,Br=null,mp.apply(yp,arguments)}function _p(e,n,t,r,o,i,a,s,l){if(gp.apply(this,arguments),Mt){if(Mt){var p=Br;Mt=!1,Br=null}else throw Error(E(198));$r||($r=!0,wi=p)}}function Vn(e){var n=e,t=e;if(e.alternate)for(;n.return;)n=n.return;else{e=n;do n=e,n.flags&4098&&(t=n.return),e=n.return;while(e)}return n.tag===3?t:null}function Bl(e){if(e.tag===13){var n=e.memoizedState;if(n===null&&(e=e.alternate,e!==null&&(n=e.memoizedState)),n!==null)return n.dehydrated}return null}function is(e){if(Vn(e)!==e)throw Error(E(188))}function hp(e){var n=e.alternate;if(!n){if(n=Vn(e),n===null)throw Error(E(188));return n!==e?null:e}for(var t=e,r=n;;){var o=t.return;if(o===null)break;var i=o.alternate;if(i===null){if(r=o.return,r!==null){t=r;continue}break}if(o.child===i.child){for(i=o.child;i;){if(i===t)return is(o),e;if(i===r)return is(o),n;i=i.sibling}throw Error(E(188))}if(t.return!==r.return)t=o,r=i;else{for(var a=!1,s=o.child;s;){if(s===t){a=!0,t=o,r=i;break}if(s===r){a=!0,r=o,t=i;break}s=s.sibling}if(!a){for(s=i.child;s;){if(s===t){a=!0,t=i,r=o;break}if(s===r){a=!0,r=i,t=o;break}s=s.sibling}if(!a)throw Error(E(189))}}if(t.alternate!==r)throw Error(E(190))}if(t.tag!==3)throw Error(E(188));return t.stateNode.current===t?e:n}function $l(e){return e=hp(e),e!==null?Hl(e):null}function Hl(e){if(e.tag===5||e.tag===6)return e;for(e=e.child;e!==null;){var n=Hl(e);if(n!==null)return n;e=e.sibling}return null}var ql=Ee.unstable_scheduleCallback,as=Ee.unstable_cancelCallback,vp=Ee.unstable_shouldYield,xp=Ee.unstable_requestPaint,Y=Ee.unstable_now,wp=Ee.unstable_getCurrentPriorityLevel,ua=Ee.unstable_ImmediatePriority,Vl=Ee.unstable_UserBlockingPriority,Hr=Ee.unstable_NormalPriority,kp=Ee.unstable_LowPriority,Gl=Ee.unstable_IdlePriority,yo=null,We=null;function Ep(e){if(We&&typeof We.onCommitFiberRoot=="function")try{We.onCommitFiberRoot(yo,e,void 0,(e.current.flags&128)===128)}catch{}}var Ue=Math.clz32?Math.clz32:Cp,Sp=Math.log,bp=Math.LN2;function Cp(e){return e>>>=0,e===0?32:31-(Sp(e)/bp|0)|0}var yr=64,gr=4194304;function It(e){switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return e&4194240;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return e&130023424;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 1073741824;default:return e}}function qr(e,n){var t=e.pendingLanes;if(t===0)return 0;var r=0,o=e.suspendedLanes,i=e.pingedLanes,a=t&268435455;if(a!==0){var s=a&~o;s!==0?r=It(s):(i&=a,i!==0&&(r=It(i)))}else a=t&~o,a!==0?r=It(a):i!==0&&(r=It(i));if(r===0)return 0;if(n!==0&&n!==r&&!(n&o)&&(o=r&-r,i=n&-n,o>=i||o===16&&(i&4194240)!==0))return n;if(r&4&&(r|=t&16),n=e.entangledLanes,n!==0)for(e=e.entanglements,n&=r;0<n;)t=31-Ue(n),o=1<<t,r|=e[t],n&=~o;return r}function Np(e,n){switch(e){case 1:case 2:case 4:return n+250;case 8:case 16:case 32:case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return n+5e3;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return-1;case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function Rp(e,n){for(var t=e.suspendedLanes,r=e.pingedLanes,o=e.expirationTimes,i=e.pendingLanes;0<i;){var a=31-Ue(i),s=1<<a,l=o[a];l===-1?(!(s&t)||s&r)&&(o[a]=Np(s,n)):l<=n&&(e.expiredLanes|=s),i&=~s}}function ki(e){return e=e.pendingLanes&-1073741825,e!==0?e:e&1073741824?1073741824:0}function Wl(){var e=yr;return yr<<=1,!(yr&4194240)&&(yr=64),e}function Do(e){for(var n=[],t=0;31>t;t++)n.push(e);return n}function sr(e,n,t){e.pendingLanes|=n,n!==536870912&&(e.suspendedLanes=0,e.pingedLanes=0),e=e.eventTimes,n=31-Ue(n),e[n]=t}function Tp(e,n){var t=e.pendingLanes&~n;e.pendingLanes=n,e.suspendedLanes=0,e.pingedLanes=0,e.expiredLanes&=n,e.mutableReadLanes&=n,e.entangledLanes&=n,n=e.entanglements;var r=e.eventTimes;for(e=e.expirationTimes;0<t;){var o=31-Ue(t),i=1<<o;n[o]=0,r[o]=-1,e[o]=-1,t&=~i}}function ca(e,n){var t=e.entangledLanes|=n;for(e=e.entanglements;t;){var r=31-Ue(t),o=1<<r;o&n|e[r]&n&&(e[r]|=n),t&=~o}}var L=0;function Kl(e){return e&=-e,1<e?4<e?e&268435455?16:536870912:4:1}var Yl,pa,Ql,Zl,Xl,Ei=!1,_r=[],vn=null,xn=null,wn=null,Gt=new Map,Wt=new Map,mn=[],Ap="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(" ");function ss(e,n){switch(e){case"focusin":case"focusout":vn=null;break;case"dragenter":case"dragleave":xn=null;break;case"mouseover":case"mouseout":wn=null;break;case"pointerover":case"pointerout":Gt.delete(n.pointerId);break;case"gotpointercapture":case"lostpointercapture":Wt.delete(n.pointerId)}}function St(e,n,t,r,o,i){return e===null||e.nativeEvent!==i?(e={blockedOn:n,domEventName:t,eventSystemFlags:r,nativeEvent:i,targetContainers:[o]},n!==null&&(n=ur(n),n!==null&&pa(n)),e):(e.eventSystemFlags|=r,n=e.targetContainers,o!==null&&n.indexOf(o)===-1&&n.push(o),e)}function Pp(e,n,t,r,o){switch(n){case"focusin":return vn=St(vn,e,n,t,r,o),!0;case"dragenter":return xn=St(xn,e,n,t,r,o),!0;case"mouseover":return wn=St(wn,e,n,t,r,o),!0;case"pointerover":var i=o.pointerId;return Gt.set(i,St(Gt.get(i)||null,e,n,t,r,o)),!0;case"gotpointercapture":return i=o.pointerId,Wt.set(i,St(Wt.get(i)||null,e,n,t,r,o)),!0}return!1}function Jl(e){var n=On(e.target);if(n!==null){var t=Vn(n);if(t!==null){if(n=t.tag,n===13){if(n=Bl(t),n!==null){e.blockedOn=n,Xl(e.priority,function(){Ql(t)});return}}else if(n===3&&t.stateNode.current.memoizedState.isDehydrated){e.blockedOn=t.tag===3?t.stateNode.containerInfo:null;return}}}e.blockedOn=null}function Ar(e){if(e.blockedOn!==null)return!1;for(var n=e.targetContainers;0<n.length;){var t=Si(e.domEventName,e.eventSystemFlags,n[0],e.nativeEvent);if(t===null){t=e.nativeEvent;var r=new t.constructor(t.type,t);hi=r,t.target.dispatchEvent(r),hi=null}else return n=ur(t),n!==null&&pa(n),e.blockedOn=t,!1;n.shift()}return!0}function ls(e,n,t){Ar(e)&&t.delete(n)}function Ip(){Ei=!1,vn!==null&&Ar(vn)&&(vn=null),xn!==null&&Ar(xn)&&(xn=null),wn!==null&&Ar(wn)&&(wn=null),Gt.forEach(ls),Wt.forEach(ls)}function bt(e,n){e.blockedOn===n&&(e.blockedOn=null,Ei||(Ei=!0,Ee.unstable_scheduleCallback(Ee.unstable_NormalPriority,Ip)))}function Kt(e){function n(o){return bt(o,e)}if(0<_r.length){bt(_r[0],e);for(var t=1;t<_r.length;t++){var r=_r[t];r.blockedOn===e&&(r.blockedOn=null)}}for(vn!==null&&bt(vn,e),xn!==null&&bt(xn,e),wn!==null&&bt(wn,e),Gt.forEach(n),Wt.forEach(n),t=0;t<mn.length;t++)r=mn[t],r.blockedOn===e&&(r.blockedOn=null);for(;0<mn.length&&(t=mn[0],t.blockedOn===null);)Jl(t),t.blockedOn===null&&mn.shift()}var ut=ln.ReactCurrentBatchConfig,Vr=!0;function Fp(e,n,t,r){var o=L,i=ut.transition;ut.transition=null;try{L=1,da(e,n,t,r)}finally{L=o,ut.transition=i}}function Op(e,n,t,r){var o=L,i=ut.transition;ut.transition=null;try{L=4,da(e,n,t,r)}finally{L=o,ut.transition=i}}function da(e,n,t,r){if(Vr){var o=Si(e,n,t,r);if(o===null)Ko(e,n,r,Gr,t),ss(e,r);else if(Pp(o,e,n,t,r))r.stopPropagation();else if(ss(e,r),n&4&&-1<Ap.indexOf(e)){for(;o!==null;){var i=ur(o);if(i!==null&&Yl(i),i=Si(e,n,t,r),i===null&&Ko(e,n,r,Gr,t),i===o)break;o=i}o!==null&&r.stopPropagation()}else Ko(e,n,r,null,t)}}var Gr=null;function Si(e,n,t,r){if(Gr=null,e=la(r),e=On(e),e!==null)if(n=Vn(e),n===null)e=null;else if(t=n.tag,t===13){if(e=Bl(n),e!==null)return e;e=null}else if(t===3){if(n.stateNode.current.memoizedState.isDehydrated)return n.tag===3?n.stateNode.containerInfo:null;e=null}else n!==e&&(e=null);return Gr=e,null}function eu(e){switch(e){case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 1;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"toggle":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 4;case"message":switch(wp()){case ua:return 1;case Vl:return 4;case Hr:case kp:return 16;case Gl:return 536870912;default:return 16}default:return 16}}var gn=null,fa=null,Pr=null;function nu(){if(Pr)return Pr;var e,n=fa,t=n.length,r,o="value"in gn?gn.value:gn.textContent,i=o.length;for(e=0;e<t&&n[e]===o[e];e++);var a=t-e;for(r=1;r<=a&&n[t-r]===o[i-r];r++);return Pr=o.slice(e,1<r?1-r:void 0)}function Ir(e){var n=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&n===13&&(e=13)):e=n,e===10&&(e=13),32<=e||e===13?e:0}function hr(){return!0}function us(){return!1}function be(e){function n(t,r,o,i,a){this._reactName=t,this._targetInst=o,this.type=r,this.nativeEvent=i,this.target=a,this.currentTarget=null;for(var s in e)e.hasOwnProperty(s)&&(t=e[s],this[s]=t?t(i):i[s]);return this.isDefaultPrevented=(i.defaultPrevented!=null?i.defaultPrevented:i.returnValue===!1)?hr:us,this.isPropagationStopped=us,this}return G(n.prototype,{preventDefault:function(){this.defaultPrevented=!0;var t=this.nativeEvent;t&&(t.preventDefault?t.preventDefault():typeof t.returnValue!="unknown"&&(t.returnValue=!1),this.isDefaultPrevented=hr)},stopPropagation:function(){var t=this.nativeEvent;t&&(t.stopPropagation?t.stopPropagation():typeof t.cancelBubble!="unknown"&&(t.cancelBubble=!0),this.isPropagationStopped=hr)},persist:function(){},isPersistent:hr}),n}var xt={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},ma=be(xt),lr=G({},xt,{view:0,detail:0}),Mp=be(lr),zo,Uo,Ct,go=G({},lr,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:ya,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==Ct&&(Ct&&e.type==="mousemove"?(zo=e.screenX-Ct.screenX,Uo=e.screenY-Ct.screenY):Uo=zo=0,Ct=e),zo)},movementY:function(e){return"movementY"in e?e.movementY:Uo}}),cs=be(go),Lp=G({},go,{dataTransfer:0}),jp=be(Lp),Dp=G({},lr,{relatedTarget:0}),Bo=be(Dp),zp=G({},xt,{animationName:0,elapsedTime:0,pseudoElement:0}),Up=be(zp),Bp=G({},xt,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),$p=be(Bp),Hp=G({},xt,{data:0}),ps=be(Hp),qp={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},Vp={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},Gp={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function Wp(e){var n=this.nativeEvent;return n.getModifierState?n.getModifierState(e):(e=Gp[e])?!!n[e]:!1}function ya(){return Wp}var Kp=G({},lr,{key:function(e){if(e.key){var n=qp[e.key]||e.key;if(n!=="Unidentified")return n}return e.type==="keypress"?(e=Ir(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?Vp[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:ya,charCode:function(e){return e.type==="keypress"?Ir(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?Ir(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),Yp=be(Kp),Qp=G({},go,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),ds=be(Qp),Zp=G({},lr,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:ya}),Xp=be(Zp),Jp=G({},xt,{propertyName:0,elapsedTime:0,pseudoElement:0}),ed=be(Jp),nd=G({},go,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),td=be(nd),rd=[9,13,27,32],ga=rn&&"CompositionEvent"in window,Lt=null;rn&&"documentMode"in document&&(Lt=document.documentMode);var od=rn&&"TextEvent"in window&&!Lt,tu=rn&&(!ga||Lt&&8<Lt&&11>=Lt),fs=" ",ms=!1;function ru(e,n){switch(e){case"keyup":return rd.indexOf(n.keyCode)!==-1;case"keydown":return n.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function ou(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var Qn=!1;function id(e,n){switch(e){case"compositionend":return ou(n);case"keypress":return n.which!==32?null:(ms=!0,fs);case"textInput":return e=n.data,e===fs&&ms?null:e;default:return null}}function ad(e,n){if(Qn)return e==="compositionend"||!ga&&ru(e,n)?(e=nu(),Pr=fa=gn=null,Qn=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(n.ctrlKey||n.altKey||n.metaKey)||n.ctrlKey&&n.altKey){if(n.char&&1<n.char.length)return n.char;if(n.which)return String.fromCharCode(n.which)}return null;case"compositionend":return tu&&n.locale!=="ko"?null:n.data;default:return null}}var sd={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function ys(e){var n=e&&e.nodeName&&e.nodeName.toLowerCase();return n==="input"?!!sd[e.type]:n==="textarea"}function iu(e,n,t,r){Ll(r),n=Wr(n,"onChange"),0<n.length&&(t=new ma("onChange","change",null,t,r),e.push({event:t,listeners:n}))}var jt=null,Yt=null;function ld(e){gu(e,0)}function _o(e){var n=Jn(e);if(Tl(n))return e}function ud(e,n){if(e==="change")return n}var au=!1;if(rn){var $o;if(rn){var Ho="oninput"in document;if(!Ho){var gs=document.createElement("div");gs.setAttribute("oninput","return;"),Ho=typeof gs.oninput=="function"}$o=Ho}else $o=!1;au=$o&&(!document.documentMode||9<document.documentMode)}function _s(){jt&&(jt.detachEvent("onpropertychange",su),Yt=jt=null)}function su(e){if(e.propertyName==="value"&&_o(Yt)){var n=[];iu(n,Yt,e,la(e)),Ul(ld,n)}}function cd(e,n,t){e==="focusin"?(_s(),jt=n,Yt=t,jt.attachEvent("onpropertychange",su)):e==="focusout"&&_s()}function pd(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return _o(Yt)}function dd(e,n){if(e==="click")return _o(n)}function fd(e,n){if(e==="input"||e==="change")return _o(n)}function md(e,n){return e===n&&(e!==0||1/e===1/n)||e!==e&&n!==n}var $e=typeof Object.is=="function"?Object.is:md;function Qt(e,n){if($e(e,n))return!0;if(typeof e!="object"||e===null||typeof n!="object"||n===null)return!1;var t=Object.keys(e),r=Object.keys(n);if(t.length!==r.length)return!1;for(r=0;r<t.length;r++){var o=t[r];if(!ai.call(n,o)||!$e(e[o],n[o]))return!1}return!0}function hs(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function vs(e,n){var t=hs(e);e=0;for(var r;t;){if(t.nodeType===3){if(r=e+t.textContent.length,e<=n&&r>=n)return{node:t,offset:n-e};e=r}e:{for(;t;){if(t.nextSibling){t=t.nextSibling;break e}t=t.parentNode}t=void 0}t=hs(t)}}function lu(e,n){return e&&n?e===n?!0:e&&e.nodeType===3?!1:n&&n.nodeType===3?lu(e,n.parentNode):"contains"in e?e.contains(n):e.compareDocumentPosition?!!(e.compareDocumentPosition(n)&16):!1:!1}function uu(){for(var e=window,n=Ur();n instanceof e.HTMLIFrameElement;){try{var t=typeof n.contentWindow.location.href=="string"}catch{t=!1}if(t)e=n.contentWindow;else break;n=Ur(e.document)}return n}function _a(e){var n=e&&e.nodeName&&e.nodeName.toLowerCase();return n&&(n==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||n==="textarea"||e.contentEditable==="true")}function yd(e){var n=uu(),t=e.focusedElem,r=e.selectionRange;if(n!==t&&t&&t.ownerDocument&&lu(t.ownerDocument.documentElement,t)){if(r!==null&&_a(t)){if(n=r.start,e=r.end,e===void 0&&(e=n),"selectionStart"in t)t.selectionStart=n,t.selectionEnd=Math.min(e,t.value.length);else if(e=(n=t.ownerDocument||document)&&n.defaultView||window,e.getSelection){e=e.getSelection();var o=t.textContent.length,i=Math.min(r.start,o);r=r.end===void 0?i:Math.min(r.end,o),!e.extend&&i>r&&(o=r,r=i,i=o),o=vs(t,i);var a=vs(t,r);o&&a&&(e.rangeCount!==1||e.anchorNode!==o.node||e.anchorOffset!==o.offset||e.focusNode!==a.node||e.focusOffset!==a.offset)&&(n=n.createRange(),n.setStart(o.node,o.offset),e.removeAllRanges(),i>r?(e.addRange(n),e.extend(a.node,a.offset)):(n.setEnd(a.node,a.offset),e.addRange(n)))}}for(n=[],e=t;e=e.parentNode;)e.nodeType===1&&n.push({element:e,left:e.scrollLeft,top:e.scrollTop});for(typeof t.focus=="function"&&t.focus(),t=0;t<n.length;t++)e=n[t],e.element.scrollLeft=e.left,e.element.scrollTop=e.top}}var gd=rn&&"documentMode"in document&&11>=document.documentMode,Zn=null,bi=null,Dt=null,Ci=!1;function xs(e,n,t){var r=t.window===t?t.document:t.nodeType===9?t:t.ownerDocument;Ci||Zn==null||Zn!==Ur(r)||(r=Zn,"selectionStart"in r&&_a(r)?r={start:r.selectionStart,end:r.selectionEnd}:(r=(r.ownerDocument&&r.ownerDocument.defaultView||window).getSelection(),r={anchorNode:r.anchorNode,anchorOffset:r.anchorOffset,focusNode:r.focusNode,focusOffset:r.focusOffset}),Dt&&Qt(Dt,r)||(Dt=r,r=Wr(bi,"onSelect"),0<r.length&&(n=new ma("onSelect","select",null,n,t),e.push({event:n,listeners:r}),n.target=Zn)))}function vr(e,n){var t={};return t[e.toLowerCase()]=n.toLowerCase(),t["Webkit"+e]="webkit"+n,t["Moz"+e]="moz"+n,t}var Xn={animationend:vr("Animation","AnimationEnd"),animationiteration:vr("Animation","AnimationIteration"),animationstart:vr("Animation","AnimationStart"),transitionend:vr("Transition","TransitionEnd")},qo={},cu={};rn&&(cu=document.createElement("div").style,"AnimationEvent"in window||(delete Xn.animationend.animation,delete Xn.animationiteration.animation,delete Xn.animationstart.animation),"TransitionEvent"in window||delete Xn.transitionend.transition);function ho(e){if(qo[e])return qo[e];if(!Xn[e])return e;var n=Xn[e],t;for(t in n)if(n.hasOwnProperty(t)&&t in cu)return qo[e]=n[t];return e}var pu=ho("animationend"),du=ho("animationiteration"),fu=ho("animationstart"),mu=ho("transitionend"),yu=new Map,ws="abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");function Tn(e,n){yu.set(e,n),qn(n,[e])}for(var Vo=0;Vo<ws.length;Vo++){var Go=ws[Vo],_d=Go.toLowerCase(),hd=Go[0].toUpperCase()+Go.slice(1);Tn(_d,"on"+hd)}Tn(pu,"onAnimationEnd");Tn(du,"onAnimationIteration");Tn(fu,"onAnimationStart");Tn("dblclick","onDoubleClick");Tn("focusin","onFocus");Tn("focusout","onBlur");Tn(mu,"onTransitionEnd");dt("onMouseEnter",["mouseout","mouseover"]);dt("onMouseLeave",["mouseout","mouseover"]);dt("onPointerEnter",["pointerout","pointerover"]);dt("onPointerLeave",["pointerout","pointerover"]);qn("onChange","change click focusin focusout input keydown keyup selectionchange".split(" "));qn("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" "));qn("onBeforeInput",["compositionend","keypress","textInput","paste"]);qn("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" "));qn("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" "));qn("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var Ft="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),vd=new Set("cancel close invalid load scroll toggle".split(" ").concat(Ft));function ks(e,n,t){var r=e.type||"unknown-event";e.currentTarget=t,_p(r,n,void 0,e),e.currentTarget=null}function gu(e,n){n=(n&4)!==0;for(var t=0;t<e.length;t++){var r=e[t],o=r.event;r=r.listeners;e:{var i=void 0;if(n)for(var a=r.length-1;0<=a;a--){var s=r[a],l=s.instance,p=s.currentTarget;if(s=s.listener,l!==i&&o.isPropagationStopped())break e;ks(o,s,p),i=l}else for(a=0;a<r.length;a++){if(s=r[a],l=s.instance,p=s.currentTarget,s=s.listener,l!==i&&o.isPropagationStopped())break e;ks(o,s,p),i=l}}}if($r)throw e=wi,$r=!1,wi=null,e}function U(e,n){var t=n[Pi];t===void 0&&(t=n[Pi]=new Set);var r=e+"__bubble";t.has(r)||(_u(n,e,2,!1),t.add(r))}function Wo(e,n,t){var r=0;n&&(r|=4),_u(t,e,r,n)}var xr="_reactListening"+Math.random().toString(36).slice(2);function Zt(e){if(!e[xr]){e[xr]=!0,Sl.forEach(function(t){t!=="selectionchange"&&(vd.has(t)||Wo(t,!1,e),Wo(t,!0,e))});var n=e.nodeType===9?e:e.ownerDocument;n===null||n[xr]||(n[xr]=!0,Wo("selectionchange",!1,n))}}function _u(e,n,t,r){switch(eu(n)){case 1:var o=Fp;break;case 4:o=Op;break;default:o=da}t=o.bind(null,n,t,e),o=void 0,!xi||n!=="touchstart"&&n!=="touchmove"&&n!=="wheel"||(o=!0),r?o!==void 0?e.addEventListener(n,t,{capture:!0,passive:o}):e.addEventListener(n,t,!0):o!==void 0?e.addEventListener(n,t,{passive:o}):e.addEventListener(n,t,!1)}function Ko(e,n,t,r,o){var i=r;if(!(n&1)&&!(n&2)&&r!==null)e:for(;;){if(r===null)return;var a=r.tag;if(a===3||a===4){var s=r.stateNode.containerInfo;if(s===o||s.nodeType===8&&s.parentNode===o)break;if(a===4)for(a=r.return;a!==null;){var l=a.tag;if((l===3||l===4)&&(l=a.stateNode.containerInfo,l===o||l.nodeType===8&&l.parentNode===o))return;a=a.return}for(;s!==null;){if(a=On(s),a===null)return;if(l=a.tag,l===5||l===6){r=i=a;continue e}s=s.parentNode}}r=r.return}Ul(function(){var p=i,g=la(t),y=[];e:{var _=yu.get(e);if(_!==void 0){var w=ma,f=e;switch(e){case"keypress":if(Ir(t)===0)break e;case"keydown":case"keyup":w=Yp;break;case"focusin":f="focus",w=Bo;break;case"focusout":f="blur",w=Bo;break;case"beforeblur":case"afterblur":w=Bo;break;case"click":if(t.button===2)break e;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":w=cs;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":w=jp;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":w=Xp;break;case pu:case du:case fu:w=Up;break;case mu:w=ed;break;case"scroll":w=Mp;break;case"wheel":w=td;break;case"copy":case"cut":case"paste":w=$p;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":w=ds}var m=(n&4)!==0,h=!m&&e==="scroll",c=m?_!==null?_+"Capture":null:_;m=[];for(var u=p,d;u!==null;){d=u;var v=d.stateNode;if(d.tag===5&&v!==null&&(d=v,c!==null&&(v=Vt(u,c),v!=null&&m.push(Xt(u,v,d)))),h)break;u=u.return}0<m.length&&(_=new w(_,f,null,t,g),y.push({event:_,listeners:m}))}}if(!(n&7)){e:{if(_=e==="mouseover"||e==="pointerover",w=e==="mouseout"||e==="pointerout",_&&t!==hi&&(f=t.relatedTarget||t.fromElement)&&(On(f)||f[on]))break e;if((w||_)&&(_=g.window===g?g:(_=g.ownerDocument)?_.defaultView||_.parentWindow:window,w?(f=t.relatedTarget||t.toElement,w=p,f=f?On(f):null,f!==null&&(h=Vn(f),f!==h||f.tag!==5&&f.tag!==6)&&(f=null)):(w=null,f=p),w!==f)){if(m=cs,v="onMouseLeave",c="onMouseEnter",u="mouse",(e==="pointerout"||e==="pointerover")&&(m=ds,v="onPointerLeave",c="onPointerEnter",u="pointer"),h=w==null?_:Jn(w),d=f==null?_:Jn(f),_=new m(v,u+"leave",w,t,g),_.target=h,_.relatedTarget=d,v=null,On(g)===p&&(m=new m(c,u+"enter",f,t,g),m.target=d,m.relatedTarget=h,v=m),h=v,w&&f)n:{for(m=w,c=f,u=0,d=m;d;d=Wn(d))u++;for(d=0,v=c;v;v=Wn(v))d++;for(;0<u-d;)m=Wn(m),u--;for(;0<d-u;)c=Wn(c),d--;for(;u--;){if(m===c||c!==null&&m===c.alternate)break n;m=Wn(m),c=Wn(c)}m=null}else m=null;w!==null&&Es(y,_,w,m,!1),f!==null&&h!==null&&Es(y,h,f,m,!0)}}e:{if(_=p?Jn(p):window,w=_.nodeName&&_.nodeName.toLowerCase(),w==="select"||w==="input"&&_.type==="file")var k=ud;else if(ys(_))if(au)k=fd;else{k=pd;var C=cd}else(w=_.nodeName)&&w.toLowerCase()==="input"&&(_.type==="checkbox"||_.type==="radio")&&(k=dd);if(k&&(k=k(e,p))){iu(y,k,t,g);break e}C&&C(e,_,p),e==="focusout"&&(C=_._wrapperState)&&C.controlled&&_.type==="number"&&fi(_,"number",_.value)}switch(C=p?Jn(p):window,e){case"focusin":(ys(C)||C.contentEditable==="true")&&(Zn=C,bi=p,Dt=null);break;case"focusout":Dt=bi=Zn=null;break;case"mousedown":Ci=!0;break;case"contextmenu":case"mouseup":case"dragend":Ci=!1,xs(y,t,g);break;case"selectionchange":if(gd)break;case"keydown":case"keyup":xs(y,t,g)}var S;if(ga)e:{switch(e){case"compositionstart":var N="onCompositionStart";break e;case"compositionend":N="onCompositionEnd";break e;case"compositionupdate":N="onCompositionUpdate";break e}N=void 0}else Qn?ru(e,t)&&(N="onCompositionEnd"):e==="keydown"&&t.keyCode===229&&(N="onCompositionStart");N&&(tu&&t.locale!=="ko"&&(Qn||N!=="onCompositionStart"?N==="onCompositionEnd"&&Qn&&(S=nu()):(gn=g,fa="value"in gn?gn.value:gn.textContent,Qn=!0)),C=Wr(p,N),0<C.length&&(N=new ps(N,e,null,t,g),y.push({event:N,listeners:C}),S?N.data=S:(S=ou(t),S!==null&&(N.data=S)))),(S=od?id(e,t):ad(e,t))&&(p=Wr(p,"onBeforeInput"),0<p.length&&(g=new ps("onBeforeInput","beforeinput",null,t,g),y.push({event:g,listeners:p}),g.data=S))}gu(y,n)})}function Xt(e,n,t){return{instance:e,listener:n,currentTarget:t}}function Wr(e,n){for(var t=n+"Capture",r=[];e!==null;){var o=e,i=o.stateNode;o.tag===5&&i!==null&&(o=i,i=Vt(e,t),i!=null&&r.unshift(Xt(e,i,o)),i=Vt(e,n),i!=null&&r.push(Xt(e,i,o))),e=e.return}return r}function Wn(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5);return e||null}function Es(e,n,t,r,o){for(var i=n._reactName,a=[];t!==null&&t!==r;){var s=t,l=s.alternate,p=s.stateNode;if(l!==null&&l===r)break;s.tag===5&&p!==null&&(s=p,o?(l=Vt(t,i),l!=null&&a.unshift(Xt(t,l,s))):o||(l=Vt(t,i),l!=null&&a.push(Xt(t,l,s)))),t=t.return}a.length!==0&&e.push({event:n,listeners:a})}var xd=/\r\n?/g,wd=/\u0000|\uFFFD/g;function Ss(e){return(typeof e=="string"?e:""+e).replace(xd,`
`).replace(wd,"")}function wr(e,n,t){if(n=Ss(n),Ss(e)!==n&&t)throw Error(E(425))}function Kr(){}var Ni=null,Ri=null;function Ti(e,n){return e==="textarea"||e==="noscript"||typeof n.children=="string"||typeof n.children=="number"||typeof n.dangerouslySetInnerHTML=="object"&&n.dangerouslySetInnerHTML!==null&&n.dangerouslySetInnerHTML.__html!=null}var Ai=typeof setTimeout=="function"?setTimeout:void 0,kd=typeof clearTimeout=="function"?clearTimeout:void 0,bs=typeof Promise=="function"?Promise:void 0,Ed=typeof queueMicrotask=="function"?queueMicrotask:typeof bs<"u"?function(e){return bs.resolve(null).then(e).catch(Sd)}:Ai;function Sd(e){setTimeout(function(){throw e})}function Yo(e,n){var t=n,r=0;do{var o=t.nextSibling;if(e.removeChild(t),o&&o.nodeType===8)if(t=o.data,t==="/$"){if(r===0){e.removeChild(o),Kt(n);return}r--}else t!=="$"&&t!=="$?"&&t!=="$!"||r++;t=o}while(t);Kt(n)}function kn(e){for(;e!=null;e=e.nextSibling){var n=e.nodeType;if(n===1||n===3)break;if(n===8){if(n=e.data,n==="$"||n==="$!"||n==="$?")break;if(n==="/$")return null}}return e}function Cs(e){e=e.previousSibling;for(var n=0;e;){if(e.nodeType===8){var t=e.data;if(t==="$"||t==="$!"||t==="$?"){if(n===0)return e;n--}else t==="/$"&&n++}e=e.previousSibling}return null}var wt=Math.random().toString(36).slice(2),Ge="__reactFiber$"+wt,Jt="__reactProps$"+wt,on="__reactContainer$"+wt,Pi="__reactEvents$"+wt,bd="__reactListeners$"+wt,Cd="__reactHandles$"+wt;function On(e){var n=e[Ge];if(n)return n;for(var t=e.parentNode;t;){if(n=t[on]||t[Ge]){if(t=n.alternate,n.child!==null||t!==null&&t.child!==null)for(e=Cs(e);e!==null;){if(t=e[Ge])return t;e=Cs(e)}return n}e=t,t=e.parentNode}return null}function ur(e){return e=e[Ge]||e[on],!e||e.tag!==5&&e.tag!==6&&e.tag!==13&&e.tag!==3?null:e}function Jn(e){if(e.tag===5||e.tag===6)return e.stateNode;throw Error(E(33))}function vo(e){return e[Jt]||null}var Ii=[],et=-1;function An(e){return{current:e}}function B(e){0>et||(e.current=Ii[et],Ii[et]=null,et--)}function D(e,n){et++,Ii[et]=e.current,e.current=n}var Rn={},ue=An(Rn),ge=An(!1),zn=Rn;function ft(e,n){var t=e.type.contextTypes;if(!t)return Rn;var r=e.stateNode;if(r&&r.__reactInternalMemoizedUnmaskedChildContext===n)return r.__reactInternalMemoizedMaskedChildContext;var o={},i;for(i in t)o[i]=n[i];return r&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=n,e.__reactInternalMemoizedMaskedChildContext=o),o}function _e(e){return e=e.childContextTypes,e!=null}function Yr(){B(ge),B(ue)}function Ns(e,n,t){if(ue.current!==Rn)throw Error(E(168));D(ue,n),D(ge,t)}function hu(e,n,t){var r=e.stateNode;if(n=n.childContextTypes,typeof r.getChildContext!="function")return t;r=r.getChildContext();for(var o in r)if(!(o in n))throw Error(E(108,cp(e)||"Unknown",o));return G({},t,r)}function Qr(e){return e=(e=e.stateNode)&&e.__reactInternalMemoizedMergedChildContext||Rn,zn=ue.current,D(ue,e),D(ge,ge.current),!0}function Rs(e,n,t){var r=e.stateNode;if(!r)throw Error(E(169));t?(e=hu(e,n,zn),r.__reactInternalMemoizedMergedChildContext=e,B(ge),B(ue),D(ue,e)):B(ge),D(ge,t)}var Je=null,xo=!1,Qo=!1;function vu(e){Je===null?Je=[e]:Je.push(e)}function Nd(e){xo=!0,vu(e)}function Pn(){if(!Qo&&Je!==null){Qo=!0;var e=0,n=L;try{var t=Je;for(L=1;e<t.length;e++){var r=t[e];do r=r(!0);while(r!==null)}Je=null,xo=!1}catch(o){throw Je!==null&&(Je=Je.slice(e+1)),ql(ua,Pn),o}finally{L=n,Qo=!1}}return null}var nt=[],tt=0,Zr=null,Xr=0,Ne=[],Re=0,Un=null,en=1,nn="";function In(e,n){nt[tt++]=Xr,nt[tt++]=Zr,Zr=e,Xr=n}function xu(e,n,t){Ne[Re++]=en,Ne[Re++]=nn,Ne[Re++]=Un,Un=e;var r=en;e=nn;var o=32-Ue(r)-1;r&=~(1<<o),t+=1;var i=32-Ue(n)+o;if(30<i){var a=o-o%5;i=(r&(1<<a)-1).toString(32),r>>=a,o-=a,en=1<<32-Ue(n)+o|t<<o|r,nn=i+e}else en=1<<i|t<<o|r,nn=e}function ha(e){e.return!==null&&(In(e,1),xu(e,1,0))}function va(e){for(;e===Zr;)Zr=nt[--tt],nt[tt]=null,Xr=nt[--tt],nt[tt]=null;for(;e===Un;)Un=Ne[--Re],Ne[Re]=null,nn=Ne[--Re],Ne[Re]=null,en=Ne[--Re],Ne[Re]=null}var ke=null,we=null,$=!1,De=null;function wu(e,n){var t=Te(5,null,null,0);t.elementType="DELETED",t.stateNode=n,t.return=e,n=e.deletions,n===null?(e.deletions=[t],e.flags|=16):n.push(t)}function Ts(e,n){switch(e.tag){case 5:var t=e.type;return n=n.nodeType!==1||t.toLowerCase()!==n.nodeName.toLowerCase()?null:n,n!==null?(e.stateNode=n,ke=e,we=kn(n.firstChild),!0):!1;case 6:return n=e.pendingProps===""||n.nodeType!==3?null:n,n!==null?(e.stateNode=n,ke=e,we=null,!0):!1;case 13:return n=n.nodeType!==8?null:n,n!==null?(t=Un!==null?{id:en,overflow:nn}:null,e.memoizedState={dehydrated:n,treeContext:t,retryLane:1073741824},t=Te(18,null,null,0),t.stateNode=n,t.return=e,e.child=t,ke=e,we=null,!0):!1;default:return!1}}function Fi(e){return(e.mode&1)!==0&&(e.flags&128)===0}function Oi(e){if($){var n=we;if(n){var t=n;if(!Ts(e,n)){if(Fi(e))throw Error(E(418));n=kn(t.nextSibling);var r=ke;n&&Ts(e,n)?wu(r,t):(e.flags=e.flags&-4097|2,$=!1,ke=e)}}else{if(Fi(e))throw Error(E(418));e.flags=e.flags&-4097|2,$=!1,ke=e}}}function As(e){for(e=e.return;e!==null&&e.tag!==5&&e.tag!==3&&e.tag!==13;)e=e.return;ke=e}function kr(e){if(e!==ke)return!1;if(!$)return As(e),$=!0,!1;var n;if((n=e.tag!==3)&&!(n=e.tag!==5)&&(n=e.type,n=n!=="head"&&n!=="body"&&!Ti(e.type,e.memoizedProps)),n&&(n=we)){if(Fi(e))throw ku(),Error(E(418));for(;n;)wu(e,n),n=kn(n.nextSibling)}if(As(e),e.tag===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(E(317));e:{for(e=e.nextSibling,n=0;e;){if(e.nodeType===8){var t=e.data;if(t==="/$"){if(n===0){we=kn(e.nextSibling);break e}n--}else t!=="$"&&t!=="$!"&&t!=="$?"||n++}e=e.nextSibling}we=null}}else we=ke?kn(e.stateNode.nextSibling):null;return!0}function ku(){for(var e=we;e;)e=kn(e.nextSibling)}function mt(){we=ke=null,$=!1}function xa(e){De===null?De=[e]:De.push(e)}var Rd=ln.ReactCurrentBatchConfig;function Nt(e,n,t){if(e=t.ref,e!==null&&typeof e!="function"&&typeof e!="object"){if(t._owner){if(t=t._owner,t){if(t.tag!==1)throw Error(E(309));var r=t.stateNode}if(!r)throw Error(E(147,e));var o=r,i=""+e;return n!==null&&n.ref!==null&&typeof n.ref=="function"&&n.ref._stringRef===i?n.ref:(n=function(a){var s=o.refs;a===null?delete s[i]:s[i]=a},n._stringRef=i,n)}if(typeof e!="string")throw Error(E(284));if(!t._owner)throw Error(E(290,e))}return e}function Er(e,n){throw e=Object.prototype.toString.call(n),Error(E(31,e==="[object Object]"?"object with keys {"+Object.keys(n).join(", ")+"}":e))}function Ps(e){var n=e._init;return n(e._payload)}function Eu(e){function n(c,u){if(e){var d=c.deletions;d===null?(c.deletions=[u],c.flags|=16):d.push(u)}}function t(c,u){if(!e)return null;for(;u!==null;)n(c,u),u=u.sibling;return null}function r(c,u){for(c=new Map;u!==null;)u.key!==null?c.set(u.key,u):c.set(u.index,u),u=u.sibling;return c}function o(c,u){return c=Cn(c,u),c.index=0,c.sibling=null,c}function i(c,u,d){return c.index=d,e?(d=c.alternate,d!==null?(d=d.index,d<u?(c.flags|=2,u):d):(c.flags|=2,u)):(c.flags|=1048576,u)}function a(c){return e&&c.alternate===null&&(c.flags|=2),c}function s(c,u,d,v){return u===null||u.tag!==6?(u=ri(d,c.mode,v),u.return=c,u):(u=o(u,d),u.return=c,u)}function l(c,u,d,v){var k=d.type;return k===Yn?g(c,u,d.props.children,v,d.key):u!==null&&(u.elementType===k||typeof k=="object"&&k!==null&&k.$$typeof===dn&&Ps(k)===u.type)?(v=o(u,d.props),v.ref=Nt(c,u,d),v.return=c,v):(v=zr(d.type,d.key,d.props,null,c.mode,v),v.ref=Nt(c,u,d),v.return=c,v)}function p(c,u,d,v){return u===null||u.tag!==4||u.stateNode.containerInfo!==d.containerInfo||u.stateNode.implementation!==d.implementation?(u=oi(d,c.mode,v),u.return=c,u):(u=o(u,d.children||[]),u.return=c,u)}function g(c,u,d,v,k){return u===null||u.tag!==7?(u=Dn(d,c.mode,v,k),u.return=c,u):(u=o(u,d),u.return=c,u)}function y(c,u,d){if(typeof u=="string"&&u!==""||typeof u=="number")return u=ri(""+u,c.mode,d),u.return=c,u;if(typeof u=="object"&&u!==null){switch(u.$$typeof){case dr:return d=zr(u.type,u.key,u.props,null,c.mode,d),d.ref=Nt(c,null,u),d.return=c,d;case Kn:return u=oi(u,c.mode,d),u.return=c,u;case dn:var v=u._init;return y(c,v(u._payload),d)}if(Pt(u)||kt(u))return u=Dn(u,c.mode,d,null),u.return=c,u;Er(c,u)}return null}function _(c,u,d,v){var k=u!==null?u.key:null;if(typeof d=="string"&&d!==""||typeof d=="number")return k!==null?null:s(c,u,""+d,v);if(typeof d=="object"&&d!==null){switch(d.$$typeof){case dr:return d.key===k?l(c,u,d,v):null;case Kn:return d.key===k?p(c,u,d,v):null;case dn:return k=d._init,_(c,u,k(d._payload),v)}if(Pt(d)||kt(d))return k!==null?null:g(c,u,d,v,null);Er(c,d)}return null}function w(c,u,d,v,k){if(typeof v=="string"&&v!==""||typeof v=="number")return c=c.get(d)||null,s(u,c,""+v,k);if(typeof v=="object"&&v!==null){switch(v.$$typeof){case dr:return c=c.get(v.key===null?d:v.key)||null,l(u,c,v,k);case Kn:return c=c.get(v.key===null?d:v.key)||null,p(u,c,v,k);case dn:var C=v._init;return w(c,u,d,C(v._payload),k)}if(Pt(v)||kt(v))return c=c.get(d)||null,g(u,c,v,k,null);Er(u,v)}return null}function f(c,u,d,v){for(var k=null,C=null,S=u,N=u=0,O=null;S!==null&&N<d.length;N++){S.index>N?(O=S,S=null):O=S.sibling;var A=_(c,S,d[N],v);if(A===null){S===null&&(S=O);break}e&&S&&A.alternate===null&&n(c,S),u=i(A,u,N),C===null?k=A:C.sibling=A,C=A,S=O}if(N===d.length)return t(c,S),$&&In(c,N),k;if(S===null){for(;N<d.length;N++)S=y(c,d[N],v),S!==null&&(u=i(S,u,N),C===null?k=S:C.sibling=S,C=S);return $&&In(c,N),k}for(S=r(c,S);N<d.length;N++)O=w(S,c,N,d[N],v),O!==null&&(e&&O.alternate!==null&&S.delete(O.key===null?N:O.key),u=i(O,u,N),C===null?k=O:C.sibling=O,C=O);return e&&S.forEach(function(K){return n(c,K)}),$&&In(c,N),k}function m(c,u,d,v){var k=kt(d);if(typeof k!="function")throw Error(E(150));if(d=k.call(d),d==null)throw Error(E(151));for(var C=k=null,S=u,N=u=0,O=null,A=d.next();S!==null&&!A.done;N++,A=d.next()){S.index>N?(O=S,S=null):O=S.sibling;var K=_(c,S,A.value,v);if(K===null){S===null&&(S=O);break}e&&S&&K.alternate===null&&n(c,S),u=i(K,u,N),C===null?k=K:C.sibling=K,C=K,S=O}if(A.done)return t(c,S),$&&In(c,N),k;if(S===null){for(;!A.done;N++,A=d.next())A=y(c,A.value,v),A!==null&&(u=i(A,u,N),C===null?k=A:C.sibling=A,C=A);return $&&In(c,N),k}for(S=r(c,S);!A.done;N++,A=d.next())A=w(S,c,N,A.value,v),A!==null&&(e&&A.alternate!==null&&S.delete(A.key===null?N:A.key),u=i(A,u,N),C===null?k=A:C.sibling=A,C=A);return e&&S.forEach(function(ie){return n(c,ie)}),$&&In(c,N),k}function h(c,u,d,v){if(typeof d=="object"&&d!==null&&d.type===Yn&&d.key===null&&(d=d.props.children),typeof d=="object"&&d!==null){switch(d.$$typeof){case dr:e:{for(var k=d.key,C=u;C!==null;){if(C.key===k){if(k=d.type,k===Yn){if(C.tag===7){t(c,C.sibling),u=o(C,d.props.children),u.return=c,c=u;break e}}else if(C.elementType===k||typeof k=="object"&&k!==null&&k.$$typeof===dn&&Ps(k)===C.type){t(c,C.sibling),u=o(C,d.props),u.ref=Nt(c,C,d),u.return=c,c=u;break e}t(c,C);break}else n(c,C);C=C.sibling}d.type===Yn?(u=Dn(d.props.children,c.mode,v,d.key),u.return=c,c=u):(v=zr(d.type,d.key,d.props,null,c.mode,v),v.ref=Nt(c,u,d),v.return=c,c=v)}return a(c);case Kn:e:{for(C=d.key;u!==null;){if(u.key===C)if(u.tag===4&&u.stateNode.containerInfo===d.containerInfo&&u.stateNode.implementation===d.implementation){t(c,u.sibling),u=o(u,d.children||[]),u.return=c,c=u;break e}else{t(c,u);break}else n(c,u);u=u.sibling}u=oi(d,c.mode,v),u.return=c,c=u}return a(c);case dn:return C=d._init,h(c,u,C(d._payload),v)}if(Pt(d))return f(c,u,d,v);if(kt(d))return m(c,u,d,v);Er(c,d)}return typeof d=="string"&&d!==""||typeof d=="number"?(d=""+d,u!==null&&u.tag===6?(t(c,u.sibling),u=o(u,d),u.return=c,c=u):(t(c,u),u=ri(d,c.mode,v),u.return=c,c=u),a(c)):t(c,u)}return h}var yt=Eu(!0),Su=Eu(!1),Jr=An(null),eo=null,rt=null,wa=null;function ka(){wa=rt=eo=null}function Ea(e){var n=Jr.current;B(Jr),e._currentValue=n}function Mi(e,n,t){for(;e!==null;){var r=e.alternate;if((e.childLanes&n)!==n?(e.childLanes|=n,r!==null&&(r.childLanes|=n)):r!==null&&(r.childLanes&n)!==n&&(r.childLanes|=n),e===t)break;e=e.return}}function ct(e,n){eo=e,wa=rt=null,e=e.dependencies,e!==null&&e.firstContext!==null&&(e.lanes&n&&(ye=!0),e.firstContext=null)}function Pe(e){var n=e._currentValue;if(wa!==e)if(e={context:e,memoizedValue:n,next:null},rt===null){if(eo===null)throw Error(E(308));rt=e,eo.dependencies={lanes:0,firstContext:e}}else rt=rt.next=e;return n}var Mn=null;function Sa(e){Mn===null?Mn=[e]:Mn.push(e)}function bu(e,n,t,r){var o=n.interleaved;return o===null?(t.next=t,Sa(n)):(t.next=o.next,o.next=t),n.interleaved=t,an(e,r)}function an(e,n){e.lanes|=n;var t=e.alternate;for(t!==null&&(t.lanes|=n),t=e,e=e.return;e!==null;)e.childLanes|=n,t=e.alternate,t!==null&&(t.childLanes|=n),t=e,e=e.return;return t.tag===3?t.stateNode:null}var fn=!1;function ba(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,interleaved:null,lanes:0},effects:null}}function Cu(e,n){e=e.updateQueue,n.updateQueue===e&&(n.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,effects:e.effects})}function tn(e,n){return{eventTime:e,lane:n,tag:0,payload:null,callback:null,next:null}}function En(e,n,t){var r=e.updateQueue;if(r===null)return null;if(r=r.shared,M&2){var o=r.pending;return o===null?n.next=n:(n.next=o.next,o.next=n),r.pending=n,an(e,t)}return o=r.interleaved,o===null?(n.next=n,Sa(r)):(n.next=o.next,o.next=n),r.interleaved=n,an(e,t)}function Fr(e,n,t){if(n=n.updateQueue,n!==null&&(n=n.shared,(t&4194240)!==0)){var r=n.lanes;r&=e.pendingLanes,t|=r,n.lanes=t,ca(e,t)}}function Is(e,n){var t=e.updateQueue,r=e.alternate;if(r!==null&&(r=r.updateQueue,t===r)){var o=null,i=null;if(t=t.firstBaseUpdate,t!==null){do{var a={eventTime:t.eventTime,lane:t.lane,tag:t.tag,payload:t.payload,callback:t.callback,next:null};i===null?o=i=a:i=i.next=a,t=t.next}while(t!==null);i===null?o=i=n:i=i.next=n}else o=i=n;t={baseState:r.baseState,firstBaseUpdate:o,lastBaseUpdate:i,shared:r.shared,effects:r.effects},e.updateQueue=t;return}e=t.lastBaseUpdate,e===null?t.firstBaseUpdate=n:e.next=n,t.lastBaseUpdate=n}function no(e,n,t,r){var o=e.updateQueue;fn=!1;var i=o.firstBaseUpdate,a=o.lastBaseUpdate,s=o.shared.pending;if(s!==null){o.shared.pending=null;var l=s,p=l.next;l.next=null,a===null?i=p:a.next=p,a=l;var g=e.alternate;g!==null&&(g=g.updateQueue,s=g.lastBaseUpdate,s!==a&&(s===null?g.firstBaseUpdate=p:s.next=p,g.lastBaseUpdate=l))}if(i!==null){var y=o.baseState;a=0,g=p=l=null,s=i;do{var _=s.lane,w=s.eventTime;if((r&_)===_){g!==null&&(g=g.next={eventTime:w,lane:0,tag:s.tag,payload:s.payload,callback:s.callback,next:null});e:{var f=e,m=s;switch(_=n,w=t,m.tag){case 1:if(f=m.payload,typeof f=="function"){y=f.call(w,y,_);break e}y=f;break e;case 3:f.flags=f.flags&-65537|128;case 0:if(f=m.payload,_=typeof f=="function"?f.call(w,y,_):f,_==null)break e;y=G({},y,_);break e;case 2:fn=!0}}s.callback!==null&&s.lane!==0&&(e.flags|=64,_=o.effects,_===null?o.effects=[s]:_.push(s))}else w={eventTime:w,lane:_,tag:s.tag,payload:s.payload,callback:s.callback,next:null},g===null?(p=g=w,l=y):g=g.next=w,a|=_;if(s=s.next,s===null){if(s=o.shared.pending,s===null)break;_=s,s=_.next,_.next=null,o.lastBaseUpdate=_,o.shared.pending=null}}while(!0);if(g===null&&(l=y),o.baseState=l,o.firstBaseUpdate=p,o.lastBaseUpdate=g,n=o.shared.interleaved,n!==null){o=n;do a|=o.lane,o=o.next;while(o!==n)}else i===null&&(o.shared.lanes=0);$n|=a,e.lanes=a,e.memoizedState=y}}function Fs(e,n,t){if(e=n.effects,n.effects=null,e!==null)for(n=0;n<e.length;n++){var r=e[n],o=r.callback;if(o!==null){if(r.callback=null,r=t,typeof o!="function")throw Error(E(191,o));o.call(r)}}}var cr={},Ke=An(cr),er=An(cr),nr=An(cr);function Ln(e){if(e===cr)throw Error(E(174));return e}function Ca(e,n){switch(D(nr,n),D(er,e),D(Ke,cr),e=n.nodeType,e){case 9:case 11:n=(n=n.documentElement)?n.namespaceURI:yi(null,"");break;default:e=e===8?n.parentNode:n,n=e.namespaceURI||null,e=e.tagName,n=yi(n,e)}B(Ke),D(Ke,n)}function gt(){B(Ke),B(er),B(nr)}function Nu(e){Ln(nr.current);var n=Ln(Ke.current),t=yi(n,e.type);n!==t&&(D(er,e),D(Ke,t))}function Na(e){er.current===e&&(B(Ke),B(er))}var q=An(0);function to(e){for(var n=e;n!==null;){if(n.tag===13){var t=n.memoizedState;if(t!==null&&(t=t.dehydrated,t===null||t.data==="$?"||t.data==="$!"))return n}else if(n.tag===19&&n.memoizedProps.revealOrder!==void 0){if(n.flags&128)return n}else if(n.child!==null){n.child.return=n,n=n.child;continue}if(n===e)break;for(;n.sibling===null;){if(n.return===null||n.return===e)return null;n=n.return}n.sibling.return=n.return,n=n.sibling}return null}var Zo=[];function Ra(){for(var e=0;e<Zo.length;e++)Zo[e]._workInProgressVersionPrimary=null;Zo.length=0}var Or=ln.ReactCurrentDispatcher,Xo=ln.ReactCurrentBatchConfig,Bn=0,V=null,X=null,ee=null,ro=!1,zt=!1,tr=0,Td=0;function ae(){throw Error(E(321))}function Ta(e,n){if(n===null)return!1;for(var t=0;t<n.length&&t<e.length;t++)if(!$e(e[t],n[t]))return!1;return!0}function Aa(e,n,t,r,o,i){if(Bn=i,V=n,n.memoizedState=null,n.updateQueue=null,n.lanes=0,Or.current=e===null||e.memoizedState===null?Fd:Od,e=t(r,o),zt){i=0;do{if(zt=!1,tr=0,25<=i)throw Error(E(301));i+=1,ee=X=null,n.updateQueue=null,Or.current=Md,e=t(r,o)}while(zt)}if(Or.current=oo,n=X!==null&&X.next!==null,Bn=0,ee=X=V=null,ro=!1,n)throw Error(E(300));return e}function Pa(){var e=tr!==0;return tr=0,e}function Ve(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return ee===null?V.memoizedState=ee=e:ee=ee.next=e,ee}function Ie(){if(X===null){var e=V.alternate;e=e!==null?e.memoizedState:null}else e=X.next;var n=ee===null?V.memoizedState:ee.next;if(n!==null)ee=n,X=e;else{if(e===null)throw Error(E(310));X=e,e={memoizedState:X.memoizedState,baseState:X.baseState,baseQueue:X.baseQueue,queue:X.queue,next:null},ee===null?V.memoizedState=ee=e:ee=ee.next=e}return ee}function rr(e,n){return typeof n=="function"?n(e):n}function Jo(e){var n=Ie(),t=n.queue;if(t===null)throw Error(E(311));t.lastRenderedReducer=e;var r=X,o=r.baseQueue,i=t.pending;if(i!==null){if(o!==null){var a=o.next;o.next=i.next,i.next=a}r.baseQueue=o=i,t.pending=null}if(o!==null){i=o.next,r=r.baseState;var s=a=null,l=null,p=i;do{var g=p.lane;if((Bn&g)===g)l!==null&&(l=l.next={lane:0,action:p.action,hasEagerState:p.hasEagerState,eagerState:p.eagerState,next:null}),r=p.hasEagerState?p.eagerState:e(r,p.action);else{var y={lane:g,action:p.action,hasEagerState:p.hasEagerState,eagerState:p.eagerState,next:null};l===null?(s=l=y,a=r):l=l.next=y,V.lanes|=g,$n|=g}p=p.next}while(p!==null&&p!==i);l===null?a=r:l.next=s,$e(r,n.memoizedState)||(ye=!0),n.memoizedState=r,n.baseState=a,n.baseQueue=l,t.lastRenderedState=r}if(e=t.interleaved,e!==null){o=e;do i=o.lane,V.lanes|=i,$n|=i,o=o.next;while(o!==e)}else o===null&&(t.lanes=0);return[n.memoizedState,t.dispatch]}function ei(e){var n=Ie(),t=n.queue;if(t===null)throw Error(E(311));t.lastRenderedReducer=e;var r=t.dispatch,o=t.pending,i=n.memoizedState;if(o!==null){t.pending=null;var a=o=o.next;do i=e(i,a.action),a=a.next;while(a!==o);$e(i,n.memoizedState)||(ye=!0),n.memoizedState=i,n.baseQueue===null&&(n.baseState=i),t.lastRenderedState=i}return[i,r]}function Ru(){}function Tu(e,n){var t=V,r=Ie(),o=n(),i=!$e(r.memoizedState,o);if(i&&(r.memoizedState=o,ye=!0),r=r.queue,Ia(Iu.bind(null,t,r,e),[e]),r.getSnapshot!==n||i||ee!==null&&ee.memoizedState.tag&1){if(t.flags|=2048,or(9,Pu.bind(null,t,r,o,n),void 0,null),ne===null)throw Error(E(349));Bn&30||Au(t,n,o)}return o}function Au(e,n,t){e.flags|=16384,e={getSnapshot:n,value:t},n=V.updateQueue,n===null?(n={lastEffect:null,stores:null},V.updateQueue=n,n.stores=[e]):(t=n.stores,t===null?n.stores=[e]:t.push(e))}function Pu(e,n,t,r){n.value=t,n.getSnapshot=r,Fu(n)&&Ou(e)}function Iu(e,n,t){return t(function(){Fu(n)&&Ou(e)})}function Fu(e){var n=e.getSnapshot;e=e.value;try{var t=n();return!$e(e,t)}catch{return!0}}function Ou(e){var n=an(e,1);n!==null&&Be(n,e,1,-1)}function Os(e){var n=Ve();return typeof e=="function"&&(e=e()),n.memoizedState=n.baseState=e,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:rr,lastRenderedState:e},n.queue=e,e=e.dispatch=Id.bind(null,V,e),[n.memoizedState,e]}function or(e,n,t,r){return e={tag:e,create:n,destroy:t,deps:r,next:null},n=V.updateQueue,n===null?(n={lastEffect:null,stores:null},V.updateQueue=n,n.lastEffect=e.next=e):(t=n.lastEffect,t===null?n.lastEffect=e.next=e:(r=t.next,t.next=e,e.next=r,n.lastEffect=e)),e}function Mu(){return Ie().memoizedState}function Mr(e,n,t,r){var o=Ve();V.flags|=e,o.memoizedState=or(1|n,t,void 0,r===void 0?null:r)}function wo(e,n,t,r){var o=Ie();r=r===void 0?null:r;var i=void 0;if(X!==null){var a=X.memoizedState;if(i=a.destroy,r!==null&&Ta(r,a.deps)){o.memoizedState=or(n,t,i,r);return}}V.flags|=e,o.memoizedState=or(1|n,t,i,r)}function Ms(e,n){return Mr(8390656,8,e,n)}function Ia(e,n){return wo(2048,8,e,n)}function Lu(e,n){return wo(4,2,e,n)}function ju(e,n){return wo(4,4,e,n)}function Du(e,n){if(typeof n=="function")return e=e(),n(e),function(){n(null)};if(n!=null)return e=e(),n.current=e,function(){n.current=null}}function zu(e,n,t){return t=t!=null?t.concat([e]):null,wo(4,4,Du.bind(null,n,e),t)}function Fa(){}function Uu(e,n){var t=Ie();n=n===void 0?null:n;var r=t.memoizedState;return r!==null&&n!==null&&Ta(n,r[1])?r[0]:(t.memoizedState=[e,n],e)}function Bu(e,n){var t=Ie();n=n===void 0?null:n;var r=t.memoizedState;return r!==null&&n!==null&&Ta(n,r[1])?r[0]:(e=e(),t.memoizedState=[e,n],e)}function $u(e,n,t){return Bn&21?($e(t,n)||(t=Wl(),V.lanes|=t,$n|=t,e.baseState=!0),n):(e.baseState&&(e.baseState=!1,ye=!0),e.memoizedState=t)}function Ad(e,n){var t=L;L=t!==0&&4>t?t:4,e(!0);var r=Xo.transition;Xo.transition={};try{e(!1),n()}finally{L=t,Xo.transition=r}}function Hu(){return Ie().memoizedState}function Pd(e,n,t){var r=bn(e);if(t={lane:r,action:t,hasEagerState:!1,eagerState:null,next:null},qu(e))Vu(n,t);else if(t=bu(e,n,t,r),t!==null){var o=pe();Be(t,e,r,o),Gu(t,n,r)}}function Id(e,n,t){var r=bn(e),o={lane:r,action:t,hasEagerState:!1,eagerState:null,next:null};if(qu(e))Vu(n,o);else{var i=e.alternate;if(e.lanes===0&&(i===null||i.lanes===0)&&(i=n.lastRenderedReducer,i!==null))try{var a=n.lastRenderedState,s=i(a,t);if(o.hasEagerState=!0,o.eagerState=s,$e(s,a)){var l=n.interleaved;l===null?(o.next=o,Sa(n)):(o.next=l.next,l.next=o),n.interleaved=o;return}}catch{}finally{}t=bu(e,n,o,r),t!==null&&(o=pe(),Be(t,e,r,o),Gu(t,n,r))}}function qu(e){var n=e.alternate;return e===V||n!==null&&n===V}function Vu(e,n){zt=ro=!0;var t=e.pending;t===null?n.next=n:(n.next=t.next,t.next=n),e.pending=n}function Gu(e,n,t){if(t&4194240){var r=n.lanes;r&=e.pendingLanes,t|=r,n.lanes=t,ca(e,t)}}var oo={readContext:Pe,useCallback:ae,useContext:ae,useEffect:ae,useImperativeHandle:ae,useInsertionEffect:ae,useLayoutEffect:ae,useMemo:ae,useReducer:ae,useRef:ae,useState:ae,useDebugValue:ae,useDeferredValue:ae,useTransition:ae,useMutableSource:ae,useSyncExternalStore:ae,useId:ae,unstable_isNewReconciler:!1},Fd={readContext:Pe,useCallback:function(e,n){return Ve().memoizedState=[e,n===void 0?null:n],e},useContext:Pe,useEffect:Ms,useImperativeHandle:function(e,n,t){return t=t!=null?t.concat([e]):null,Mr(4194308,4,Du.bind(null,n,e),t)},useLayoutEffect:function(e,n){return Mr(4194308,4,e,n)},useInsertionEffect:function(e,n){return Mr(4,2,e,n)},useMemo:function(e,n){var t=Ve();return n=n===void 0?null:n,e=e(),t.memoizedState=[e,n],e},useReducer:function(e,n,t){var r=Ve();return n=t!==void 0?t(n):n,r.memoizedState=r.baseState=n,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:n},r.queue=e,e=e.dispatch=Pd.bind(null,V,e),[r.memoizedState,e]},useRef:function(e){var n=Ve();return e={current:e},n.memoizedState=e},useState:Os,useDebugValue:Fa,useDeferredValue:function(e){return Ve().memoizedState=e},useTransition:function(){var e=Os(!1),n=e[0];return e=Ad.bind(null,e[1]),Ve().memoizedState=e,[n,e]},useMutableSource:function(){},useSyncExternalStore:function(e,n,t){var r=V,o=Ve();if($){if(t===void 0)throw Error(E(407));t=t()}else{if(t=n(),ne===null)throw Error(E(349));Bn&30||Au(r,n,t)}o.memoizedState=t;var i={value:t,getSnapshot:n};return o.queue=i,Ms(Iu.bind(null,r,i,e),[e]),r.flags|=2048,or(9,Pu.bind(null,r,i,t,n),void 0,null),t},useId:function(){var e=Ve(),n=ne.identifierPrefix;if($){var t=nn,r=en;t=(r&~(1<<32-Ue(r)-1)).toString(32)+t,n=":"+n+"R"+t,t=tr++,0<t&&(n+="H"+t.toString(32)),n+=":"}else t=Td++,n=":"+n+"r"+t.toString(32)+":";return e.memoizedState=n},unstable_isNewReconciler:!1},Od={readContext:Pe,useCallback:Uu,useContext:Pe,useEffect:Ia,useImperativeHandle:zu,useInsertionEffect:Lu,useLayoutEffect:ju,useMemo:Bu,useReducer:Jo,useRef:Mu,useState:function(){return Jo(rr)},useDebugValue:Fa,useDeferredValue:function(e){var n=Ie();return $u(n,X.memoizedState,e)},useTransition:function(){var e=Jo(rr)[0],n=Ie().memoizedState;return[e,n]},useMutableSource:Ru,useSyncExternalStore:Tu,useId:Hu,unstable_isNewReconciler:!1},Md={readContext:Pe,useCallback:Uu,useContext:Pe,useEffect:Ia,useImperativeHandle:zu,useInsertionEffect:Lu,useLayoutEffect:ju,useMemo:Bu,useReducer:ei,useRef:Mu,useState:function(){return ei(rr)},useDebugValue:Fa,useDeferredValue:function(e){var n=Ie();return X===null?n.memoizedState=e:$u(n,X.memoizedState,e)},useTransition:function(){var e=ei(rr)[0],n=Ie().memoizedState;return[e,n]},useMutableSource:Ru,useSyncExternalStore:Tu,useId:Hu,unstable_isNewReconciler:!1};function Le(e,n){if(e&&e.defaultProps){n=G({},n),e=e.defaultProps;for(var t in e)n[t]===void 0&&(n[t]=e[t]);return n}return n}function Li(e,n,t,r){n=e.memoizedState,t=t(r,n),t=t==null?n:G({},n,t),e.memoizedState=t,e.lanes===0&&(e.updateQueue.baseState=t)}var ko={isMounted:function(e){return(e=e._reactInternals)?Vn(e)===e:!1},enqueueSetState:function(e,n,t){e=e._reactInternals;var r=pe(),o=bn(e),i=tn(r,o);i.payload=n,t!=null&&(i.callback=t),n=En(e,i,o),n!==null&&(Be(n,e,o,r),Fr(n,e,o))},enqueueReplaceState:function(e,n,t){e=e._reactInternals;var r=pe(),o=bn(e),i=tn(r,o);i.tag=1,i.payload=n,t!=null&&(i.callback=t),n=En(e,i,o),n!==null&&(Be(n,e,o,r),Fr(n,e,o))},enqueueForceUpdate:function(e,n){e=e._reactInternals;var t=pe(),r=bn(e),o=tn(t,r);o.tag=2,n!=null&&(o.callback=n),n=En(e,o,r),n!==null&&(Be(n,e,r,t),Fr(n,e,r))}};function Ls(e,n,t,r,o,i,a){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(r,i,a):n.prototype&&n.prototype.isPureReactComponent?!Qt(t,r)||!Qt(o,i):!0}function Wu(e,n,t){var r=!1,o=Rn,i=n.contextType;return typeof i=="object"&&i!==null?i=Pe(i):(o=_e(n)?zn:ue.current,r=n.contextTypes,i=(r=r!=null)?ft(e,o):Rn),n=new n(t,i),e.memoizedState=n.state!==null&&n.state!==void 0?n.state:null,n.updater=ko,e.stateNode=n,n._reactInternals=e,r&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=o,e.__reactInternalMemoizedMaskedChildContext=i),n}function js(e,n,t,r){e=n.state,typeof n.componentWillReceiveProps=="function"&&n.componentWillReceiveProps(t,r),typeof n.UNSAFE_componentWillReceiveProps=="function"&&n.UNSAFE_componentWillReceiveProps(t,r),n.state!==e&&ko.enqueueReplaceState(n,n.state,null)}function ji(e,n,t,r){var o=e.stateNode;o.props=t,o.state=e.memoizedState,o.refs={},ba(e);var i=n.contextType;typeof i=="object"&&i!==null?o.context=Pe(i):(i=_e(n)?zn:ue.current,o.context=ft(e,i)),o.state=e.memoizedState,i=n.getDerivedStateFromProps,typeof i=="function"&&(Li(e,n,i,t),o.state=e.memoizedState),typeof n.getDerivedStateFromProps=="function"||typeof o.getSnapshotBeforeUpdate=="function"||typeof o.UNSAFE_componentWillMount!="function"&&typeof o.componentWillMount!="function"||(n=o.state,typeof o.componentWillMount=="function"&&o.componentWillMount(),typeof o.UNSAFE_componentWillMount=="function"&&o.UNSAFE_componentWillMount(),n!==o.state&&ko.enqueueReplaceState(o,o.state,null),no(e,t,o,r),o.state=e.memoizedState),typeof o.componentDidMount=="function"&&(e.flags|=4194308)}function _t(e,n){try{var t="",r=n;do t+=up(r),r=r.return;while(r);var o=t}catch(i){o=`
Error generating stack: `+i.message+`
`+i.stack}return{value:e,source:n,stack:o,digest:null}}function ni(e,n,t){return{value:e,source:null,stack:t??null,digest:n??null}}function Di(e,n){try{console.error(n.value)}catch(t){setTimeout(function(){throw t})}}var Ld=typeof WeakMap=="function"?WeakMap:Map;function Ku(e,n,t){t=tn(-1,t),t.tag=3,t.payload={element:null};var r=n.value;return t.callback=function(){ao||(ao=!0,Ki=r),Di(e,n)},t}function Yu(e,n,t){t=tn(-1,t),t.tag=3;var r=e.type.getDerivedStateFromError;if(typeof r=="function"){var o=n.value;t.payload=function(){return r(o)},t.callback=function(){Di(e,n)}}var i=e.stateNode;return i!==null&&typeof i.componentDidCatch=="function"&&(t.callback=function(){Di(e,n),typeof r!="function"&&(Sn===null?Sn=new Set([this]):Sn.add(this));var a=n.stack;this.componentDidCatch(n.value,{componentStack:a!==null?a:""})}),t}function Ds(e,n,t){var r=e.pingCache;if(r===null){r=e.pingCache=new Ld;var o=new Set;r.set(n,o)}else o=r.get(n),o===void 0&&(o=new Set,r.set(n,o));o.has(t)||(o.add(t),e=Qd.bind(null,e,n,t),n.then(e,e))}function zs(e){do{var n;if((n=e.tag===13)&&(n=e.memoizedState,n=n!==null?n.dehydrated!==null:!0),n)return e;e=e.return}while(e!==null);return null}function Us(e,n,t,r,o){return e.mode&1?(e.flags|=65536,e.lanes=o,e):(e===n?e.flags|=65536:(e.flags|=128,t.flags|=131072,t.flags&=-52805,t.tag===1&&(t.alternate===null?t.tag=17:(n=tn(-1,1),n.tag=2,En(t,n,1))),t.lanes|=1),e)}var jd=ln.ReactCurrentOwner,ye=!1;function ce(e,n,t,r){n.child=e===null?Su(n,null,t,r):yt(n,e.child,t,r)}function Bs(e,n,t,r,o){t=t.render;var i=n.ref;return ct(n,o),r=Aa(e,n,t,r,i,o),t=Pa(),e!==null&&!ye?(n.updateQueue=e.updateQueue,n.flags&=-2053,e.lanes&=~o,sn(e,n,o)):($&&t&&ha(n),n.flags|=1,ce(e,n,r,o),n.child)}function $s(e,n,t,r,o){if(e===null){var i=t.type;return typeof i=="function"&&!Ba(i)&&i.defaultProps===void 0&&t.compare===null&&t.defaultProps===void 0?(n.tag=15,n.type=i,Qu(e,n,i,r,o)):(e=zr(t.type,null,r,n,n.mode,o),e.ref=n.ref,e.return=n,n.child=e)}if(i=e.child,!(e.lanes&o)){var a=i.memoizedProps;if(t=t.compare,t=t!==null?t:Qt,t(a,r)&&e.ref===n.ref)return sn(e,n,o)}return n.flags|=1,e=Cn(i,r),e.ref=n.ref,e.return=n,n.child=e}function Qu(e,n,t,r,o){if(e!==null){var i=e.memoizedProps;if(Qt(i,r)&&e.ref===n.ref)if(ye=!1,n.pendingProps=r=i,(e.lanes&o)!==0)e.flags&131072&&(ye=!0);else return n.lanes=e.lanes,sn(e,n,o)}return zi(e,n,t,r,o)}function Zu(e,n,t){var r=n.pendingProps,o=r.children,i=e!==null?e.memoizedState:null;if(r.mode==="hidden")if(!(n.mode&1))n.memoizedState={baseLanes:0,cachePool:null,transitions:null},D(it,xe),xe|=t;else{if(!(t&1073741824))return e=i!==null?i.baseLanes|t:t,n.lanes=n.childLanes=1073741824,n.memoizedState={baseLanes:e,cachePool:null,transitions:null},n.updateQueue=null,D(it,xe),xe|=e,null;n.memoizedState={baseLanes:0,cachePool:null,transitions:null},r=i!==null?i.baseLanes:t,D(it,xe),xe|=r}else i!==null?(r=i.baseLanes|t,n.memoizedState=null):r=t,D(it,xe),xe|=r;return ce(e,n,o,t),n.child}function Xu(e,n){var t=n.ref;(e===null&&t!==null||e!==null&&e.ref!==t)&&(n.flags|=512,n.flags|=2097152)}function zi(e,n,t,r,o){var i=_e(t)?zn:ue.current;return i=ft(n,i),ct(n,o),t=Aa(e,n,t,r,i,o),r=Pa(),e!==null&&!ye?(n.updateQueue=e.updateQueue,n.flags&=-2053,e.lanes&=~o,sn(e,n,o)):($&&r&&ha(n),n.flags|=1,ce(e,n,t,o),n.child)}function Hs(e,n,t,r,o){if(_e(t)){var i=!0;Qr(n)}else i=!1;if(ct(n,o),n.stateNode===null)Lr(e,n),Wu(n,t,r),ji(n,t,r,o),r=!0;else if(e===null){var a=n.stateNode,s=n.memoizedProps;a.props=s;var l=a.context,p=t.contextType;typeof p=="object"&&p!==null?p=Pe(p):(p=_e(t)?zn:ue.current,p=ft(n,p));var g=t.getDerivedStateFromProps,y=typeof g=="function"||typeof a.getSnapshotBeforeUpdate=="function";y||typeof a.UNSAFE_componentWillReceiveProps!="function"&&typeof a.componentWillReceiveProps!="function"||(s!==r||l!==p)&&js(n,a,r,p),fn=!1;var _=n.memoizedState;a.state=_,no(n,r,a,o),l=n.memoizedState,s!==r||_!==l||ge.current||fn?(typeof g=="function"&&(Li(n,t,g,r),l=n.memoizedState),(s=fn||Ls(n,t,s,r,_,l,p))?(y||typeof a.UNSAFE_componentWillMount!="function"&&typeof a.componentWillMount!="function"||(typeof a.componentWillMount=="function"&&a.componentWillMount(),typeof a.UNSAFE_componentWillMount=="function"&&a.UNSAFE_componentWillMount()),typeof a.componentDidMount=="function"&&(n.flags|=4194308)):(typeof a.componentDidMount=="function"&&(n.flags|=4194308),n.memoizedProps=r,n.memoizedState=l),a.props=r,a.state=l,a.context=p,r=s):(typeof a.componentDidMount=="function"&&(n.flags|=4194308),r=!1)}else{a=n.stateNode,Cu(e,n),s=n.memoizedProps,p=n.type===n.elementType?s:Le(n.type,s),a.props=p,y=n.pendingProps,_=a.context,l=t.contextType,typeof l=="object"&&l!==null?l=Pe(l):(l=_e(t)?zn:ue.current,l=ft(n,l));var w=t.getDerivedStateFromProps;(g=typeof w=="function"||typeof a.getSnapshotBeforeUpdate=="function")||typeof a.UNSAFE_componentWillReceiveProps!="function"&&typeof a.componentWillReceiveProps!="function"||(s!==y||_!==l)&&js(n,a,r,l),fn=!1,_=n.memoizedState,a.state=_,no(n,r,a,o);var f=n.memoizedState;s!==y||_!==f||ge.current||fn?(typeof w=="function"&&(Li(n,t,w,r),f=n.memoizedState),(p=fn||Ls(n,t,p,r,_,f,l)||!1)?(g||typeof a.UNSAFE_componentWillUpdate!="function"&&typeof a.componentWillUpdate!="function"||(typeof a.componentWillUpdate=="function"&&a.componentWillUpdate(r,f,l),typeof a.UNSAFE_componentWillUpdate=="function"&&a.UNSAFE_componentWillUpdate(r,f,l)),typeof a.componentDidUpdate=="function"&&(n.flags|=4),typeof a.getSnapshotBeforeUpdate=="function"&&(n.flags|=1024)):(typeof a.componentDidUpdate!="function"||s===e.memoizedProps&&_===e.memoizedState||(n.flags|=4),typeof a.getSnapshotBeforeUpdate!="function"||s===e.memoizedProps&&_===e.memoizedState||(n.flags|=1024),n.memoizedProps=r,n.memoizedState=f),a.props=r,a.state=f,a.context=l,r=p):(typeof a.componentDidUpdate!="function"||s===e.memoizedProps&&_===e.memoizedState||(n.flags|=4),typeof a.getSnapshotBeforeUpdate!="function"||s===e.memoizedProps&&_===e.memoizedState||(n.flags|=1024),r=!1)}return Ui(e,n,t,r,i,o)}function Ui(e,n,t,r,o,i){Xu(e,n);var a=(n.flags&128)!==0;if(!r&&!a)return o&&Rs(n,t,!1),sn(e,n,i);r=n.stateNode,jd.current=n;var s=a&&typeof t.getDerivedStateFromError!="function"?null:r.render();return n.flags|=1,e!==null&&a?(n.child=yt(n,e.child,null,i),n.child=yt(n,null,s,i)):ce(e,n,s,i),n.memoizedState=r.state,o&&Rs(n,t,!0),n.child}function Ju(e){var n=e.stateNode;n.pendingContext?Ns(e,n.pendingContext,n.pendingContext!==n.context):n.context&&Ns(e,n.context,!1),Ca(e,n.containerInfo)}function qs(e,n,t,r,o){return mt(),xa(o),n.flags|=256,ce(e,n,t,r),n.child}var Bi={dehydrated:null,treeContext:null,retryLane:0};function $i(e){return{baseLanes:e,cachePool:null,transitions:null}}function ec(e,n,t){var r=n.pendingProps,o=q.current,i=!1,a=(n.flags&128)!==0,s;if((s=a)||(s=e!==null&&e.memoizedState===null?!1:(o&2)!==0),s?(i=!0,n.flags&=-129):(e===null||e.memoizedState!==null)&&(o|=1),D(q,o&1),e===null)return Oi(n),e=n.memoizedState,e!==null&&(e=e.dehydrated,e!==null)?(n.mode&1?e.data==="$!"?n.lanes=8:n.lanes=1073741824:n.lanes=1,null):(a=r.children,e=r.fallback,i?(r=n.mode,i=n.child,a={mode:"hidden",children:a},!(r&1)&&i!==null?(i.childLanes=0,i.pendingProps=a):i=bo(a,r,0,null),e=Dn(e,r,t,null),i.return=n,e.return=n,i.sibling=e,n.child=i,n.child.memoizedState=$i(t),n.memoizedState=Bi,e):Oa(n,a));if(o=e.memoizedState,o!==null&&(s=o.dehydrated,s!==null))return Dd(e,n,a,r,s,o,t);if(i){i=r.fallback,a=n.mode,o=e.child,s=o.sibling;var l={mode:"hidden",children:r.children};return!(a&1)&&n.child!==o?(r=n.child,r.childLanes=0,r.pendingProps=l,n.deletions=null):(r=Cn(o,l),r.subtreeFlags=o.subtreeFlags&14680064),s!==null?i=Cn(s,i):(i=Dn(i,a,t,null),i.flags|=2),i.return=n,r.return=n,r.sibling=i,n.child=r,r=i,i=n.child,a=e.child.memoizedState,a=a===null?$i(t):{baseLanes:a.baseLanes|t,cachePool:null,transitions:a.transitions},i.memoizedState=a,i.childLanes=e.childLanes&~t,n.memoizedState=Bi,r}return i=e.child,e=i.sibling,r=Cn(i,{mode:"visible",children:r.children}),!(n.mode&1)&&(r.lanes=t),r.return=n,r.sibling=null,e!==null&&(t=n.deletions,t===null?(n.deletions=[e],n.flags|=16):t.push(e)),n.child=r,n.memoizedState=null,r}function Oa(e,n){return n=bo({mode:"visible",children:n},e.mode,0,null),n.return=e,e.child=n}function Sr(e,n,t,r){return r!==null&&xa(r),yt(n,e.child,null,t),e=Oa(n,n.pendingProps.children),e.flags|=2,n.memoizedState=null,e}function Dd(e,n,t,r,o,i,a){if(t)return n.flags&256?(n.flags&=-257,r=ni(Error(E(422))),Sr(e,n,a,r)):n.memoizedState!==null?(n.child=e.child,n.flags|=128,null):(i=r.fallback,o=n.mode,r=bo({mode:"visible",children:r.children},o,0,null),i=Dn(i,o,a,null),i.flags|=2,r.return=n,i.return=n,r.sibling=i,n.child=r,n.mode&1&&yt(n,e.child,null,a),n.child.memoizedState=$i(a),n.memoizedState=Bi,i);if(!(n.mode&1))return Sr(e,n,a,null);if(o.data==="$!"){if(r=o.nextSibling&&o.nextSibling.dataset,r)var s=r.dgst;return r=s,i=Error(E(419)),r=ni(i,r,void 0),Sr(e,n,a,r)}if(s=(a&e.childLanes)!==0,ye||s){if(r=ne,r!==null){switch(a&-a){case 4:o=2;break;case 16:o=8;break;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:o=32;break;case 536870912:o=268435456;break;default:o=0}o=o&(r.suspendedLanes|a)?0:o,o!==0&&o!==i.retryLane&&(i.retryLane=o,an(e,o),Be(r,e,o,-1))}return Ua(),r=ni(Error(E(421))),Sr(e,n,a,r)}return o.data==="$?"?(n.flags|=128,n.child=e.child,n=Zd.bind(null,e),o._reactRetry=n,null):(e=i.treeContext,we=kn(o.nextSibling),ke=n,$=!0,De=null,e!==null&&(Ne[Re++]=en,Ne[Re++]=nn,Ne[Re++]=Un,en=e.id,nn=e.overflow,Un=n),n=Oa(n,r.children),n.flags|=4096,n)}function Vs(e,n,t){e.lanes|=n;var r=e.alternate;r!==null&&(r.lanes|=n),Mi(e.return,n,t)}function ti(e,n,t,r,o){var i=e.memoizedState;i===null?e.memoizedState={isBackwards:n,rendering:null,renderingStartTime:0,last:r,tail:t,tailMode:o}:(i.isBackwards=n,i.rendering=null,i.renderingStartTime=0,i.last=r,i.tail=t,i.tailMode=o)}function nc(e,n,t){var r=n.pendingProps,o=r.revealOrder,i=r.tail;if(ce(e,n,r.children,t),r=q.current,r&2)r=r&1|2,n.flags|=128;else{if(e!==null&&e.flags&128)e:for(e=n.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&Vs(e,t,n);else if(e.tag===19)Vs(e,t,n);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===n)break e;for(;e.sibling===null;){if(e.return===null||e.return===n)break e;e=e.return}e.sibling.return=e.return,e=e.sibling}r&=1}if(D(q,r),!(n.mode&1))n.memoizedState=null;else switch(o){case"forwards":for(t=n.child,o=null;t!==null;)e=t.alternate,e!==null&&to(e)===null&&(o=t),t=t.sibling;t=o,t===null?(o=n.child,n.child=null):(o=t.sibling,t.sibling=null),ti(n,!1,o,t,i);break;case"backwards":for(t=null,o=n.child,n.child=null;o!==null;){if(e=o.alternate,e!==null&&to(e)===null){n.child=o;break}e=o.sibling,o.sibling=t,t=o,o=e}ti(n,!0,t,null,i);break;case"together":ti(n,!1,null,null,void 0);break;default:n.memoizedState=null}return n.child}function Lr(e,n){!(n.mode&1)&&e!==null&&(e.alternate=null,n.alternate=null,n.flags|=2)}function sn(e,n,t){if(e!==null&&(n.dependencies=e.dependencies),$n|=n.lanes,!(t&n.childLanes))return null;if(e!==null&&n.child!==e.child)throw Error(E(153));if(n.child!==null){for(e=n.child,t=Cn(e,e.pendingProps),n.child=t,t.return=n;e.sibling!==null;)e=e.sibling,t=t.sibling=Cn(e,e.pendingProps),t.return=n;t.sibling=null}return n.child}function zd(e,n,t){switch(n.tag){case 3:Ju(n),mt();break;case 5:Nu(n);break;case 1:_e(n.type)&&Qr(n);break;case 4:Ca(n,n.stateNode.containerInfo);break;case 10:var r=n.type._context,o=n.memoizedProps.value;D(Jr,r._currentValue),r._currentValue=o;break;case 13:if(r=n.memoizedState,r!==null)return r.dehydrated!==null?(D(q,q.current&1),n.flags|=128,null):t&n.child.childLanes?ec(e,n,t):(D(q,q.current&1),e=sn(e,n,t),e!==null?e.sibling:null);D(q,q.current&1);break;case 19:if(r=(t&n.childLanes)!==0,e.flags&128){if(r)return nc(e,n,t);n.flags|=128}if(o=n.memoizedState,o!==null&&(o.rendering=null,o.tail=null,o.lastEffect=null),D(q,q.current),r)break;return null;case 22:case 23:return n.lanes=0,Zu(e,n,t)}return sn(e,n,t)}var tc,Hi,rc,oc;tc=function(e,n){for(var t=n.child;t!==null;){if(t.tag===5||t.tag===6)e.appendChild(t.stateNode);else if(t.tag!==4&&t.child!==null){t.child.return=t,t=t.child;continue}if(t===n)break;for(;t.sibling===null;){if(t.return===null||t.return===n)return;t=t.return}t.sibling.return=t.return,t=t.sibling}};Hi=function(){};rc=function(e,n,t,r){var o=e.memoizedProps;if(o!==r){e=n.stateNode,Ln(Ke.current);var i=null;switch(t){case"input":o=pi(e,o),r=pi(e,r),i=[];break;case"select":o=G({},o,{value:void 0}),r=G({},r,{value:void 0}),i=[];break;case"textarea":o=mi(e,o),r=mi(e,r),i=[];break;default:typeof o.onClick!="function"&&typeof r.onClick=="function"&&(e.onclick=Kr)}gi(t,r);var a;t=null;for(p in o)if(!r.hasOwnProperty(p)&&o.hasOwnProperty(p)&&o[p]!=null)if(p==="style"){var s=o[p];for(a in s)s.hasOwnProperty(a)&&(t||(t={}),t[a]="")}else p!=="dangerouslySetInnerHTML"&&p!=="children"&&p!=="suppressContentEditableWarning"&&p!=="suppressHydrationWarning"&&p!=="autoFocus"&&(Ht.hasOwnProperty(p)?i||(i=[]):(i=i||[]).push(p,null));for(p in r){var l=r[p];if(s=o!=null?o[p]:void 0,r.hasOwnProperty(p)&&l!==s&&(l!=null||s!=null))if(p==="style")if(s){for(a in s)!s.hasOwnProperty(a)||l&&l.hasOwnProperty(a)||(t||(t={}),t[a]="");for(a in l)l.hasOwnProperty(a)&&s[a]!==l[a]&&(t||(t={}),t[a]=l[a])}else t||(i||(i=[]),i.push(p,t)),t=l;else p==="dangerouslySetInnerHTML"?(l=l?l.__html:void 0,s=s?s.__html:void 0,l!=null&&s!==l&&(i=i||[]).push(p,l)):p==="children"?typeof l!="string"&&typeof l!="number"||(i=i||[]).push(p,""+l):p!=="suppressContentEditableWarning"&&p!=="suppressHydrationWarning"&&(Ht.hasOwnProperty(p)?(l!=null&&p==="onScroll"&&U("scroll",e),i||s===l||(i=[])):(i=i||[]).push(p,l))}t&&(i=i||[]).push("style",t);var p=i;(n.updateQueue=p)&&(n.flags|=4)}};oc=function(e,n,t,r){t!==r&&(n.flags|=4)};function Rt(e,n){if(!$)switch(e.tailMode){case"hidden":n=e.tail;for(var t=null;n!==null;)n.alternate!==null&&(t=n),n=n.sibling;t===null?e.tail=null:t.sibling=null;break;case"collapsed":t=e.tail;for(var r=null;t!==null;)t.alternate!==null&&(r=t),t=t.sibling;r===null?n||e.tail===null?e.tail=null:e.tail.sibling=null:r.sibling=null}}function se(e){var n=e.alternate!==null&&e.alternate.child===e.child,t=0,r=0;if(n)for(var o=e.child;o!==null;)t|=o.lanes|o.childLanes,r|=o.subtreeFlags&14680064,r|=o.flags&14680064,o.return=e,o=o.sibling;else for(o=e.child;o!==null;)t|=o.lanes|o.childLanes,r|=o.subtreeFlags,r|=o.flags,o.return=e,o=o.sibling;return e.subtreeFlags|=r,e.childLanes=t,n}function Ud(e,n,t){var r=n.pendingProps;switch(va(n),n.tag){case 2:case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return se(n),null;case 1:return _e(n.type)&&Yr(),se(n),null;case 3:return r=n.stateNode,gt(),B(ge),B(ue),Ra(),r.pendingContext&&(r.context=r.pendingContext,r.pendingContext=null),(e===null||e.child===null)&&(kr(n)?n.flags|=4:e===null||e.memoizedState.isDehydrated&&!(n.flags&256)||(n.flags|=1024,De!==null&&(Zi(De),De=null))),Hi(e,n),se(n),null;case 5:Na(n);var o=Ln(nr.current);if(t=n.type,e!==null&&n.stateNode!=null)rc(e,n,t,r,o),e.ref!==n.ref&&(n.flags|=512,n.flags|=2097152);else{if(!r){if(n.stateNode===null)throw Error(E(166));return se(n),null}if(e=Ln(Ke.current),kr(n)){r=n.stateNode,t=n.type;var i=n.memoizedProps;switch(r[Ge]=n,r[Jt]=i,e=(n.mode&1)!==0,t){case"dialog":U("cancel",r),U("close",r);break;case"iframe":case"object":case"embed":U("load",r);break;case"video":case"audio":for(o=0;o<Ft.length;o++)U(Ft[o],r);break;case"source":U("error",r);break;case"img":case"image":case"link":U("error",r),U("load",r);break;case"details":U("toggle",r);break;case"input":es(r,i),U("invalid",r);break;case"select":r._wrapperState={wasMultiple:!!i.multiple},U("invalid",r);break;case"textarea":ts(r,i),U("invalid",r)}gi(t,i),o=null;for(var a in i)if(i.hasOwnProperty(a)){var s=i[a];a==="children"?typeof s=="string"?r.textContent!==s&&(i.suppressHydrationWarning!==!0&&wr(r.textContent,s,e),o=["children",s]):typeof s=="number"&&r.textContent!==""+s&&(i.suppressHydrationWarning!==!0&&wr(r.textContent,s,e),o=["children",""+s]):Ht.hasOwnProperty(a)&&s!=null&&a==="onScroll"&&U("scroll",r)}switch(t){case"input":fr(r),ns(r,i,!0);break;case"textarea":fr(r),rs(r);break;case"select":case"option":break;default:typeof i.onClick=="function"&&(r.onclick=Kr)}r=o,n.updateQueue=r,r!==null&&(n.flags|=4)}else{a=o.nodeType===9?o:o.ownerDocument,e==="http://www.w3.org/1999/xhtml"&&(e=Il(t)),e==="http://www.w3.org/1999/xhtml"?t==="script"?(e=a.createElement("div"),e.innerHTML="<script><\/script>",e=e.removeChild(e.firstChild)):typeof r.is=="string"?e=a.createElement(t,{is:r.is}):(e=a.createElement(t),t==="select"&&(a=e,r.multiple?a.multiple=!0:r.size&&(a.size=r.size))):e=a.createElementNS(e,t),e[Ge]=n,e[Jt]=r,tc(e,n,!1,!1),n.stateNode=e;e:{switch(a=_i(t,r),t){case"dialog":U("cancel",e),U("close",e),o=r;break;case"iframe":case"object":case"embed":U("load",e),o=r;break;case"video":case"audio":for(o=0;o<Ft.length;o++)U(Ft[o],e);o=r;break;case"source":U("error",e),o=r;break;case"img":case"image":case"link":U("error",e),U("load",e),o=r;break;case"details":U("toggle",e),o=r;break;case"input":es(e,r),o=pi(e,r),U("invalid",e);break;case"option":o=r;break;case"select":e._wrapperState={wasMultiple:!!r.multiple},o=G({},r,{value:void 0}),U("invalid",e);break;case"textarea":ts(e,r),o=mi(e,r),U("invalid",e);break;default:o=r}gi(t,o),s=o;for(i in s)if(s.hasOwnProperty(i)){var l=s[i];i==="style"?Ml(e,l):i==="dangerouslySetInnerHTML"?(l=l?l.__html:void 0,l!=null&&Fl(e,l)):i==="children"?typeof l=="string"?(t!=="textarea"||l!=="")&&qt(e,l):typeof l=="number"&&qt(e,""+l):i!=="suppressContentEditableWarning"&&i!=="suppressHydrationWarning"&&i!=="autoFocus"&&(Ht.hasOwnProperty(i)?l!=null&&i==="onScroll"&&U("scroll",e):l!=null&&oa(e,i,l,a))}switch(t){case"input":fr(e),ns(e,r,!1);break;case"textarea":fr(e),rs(e);break;case"option":r.value!=null&&e.setAttribute("value",""+Nn(r.value));break;case"select":e.multiple=!!r.multiple,i=r.value,i!=null?at(e,!!r.multiple,i,!1):r.defaultValue!=null&&at(e,!!r.multiple,r.defaultValue,!0);break;default:typeof o.onClick=="function"&&(e.onclick=Kr)}switch(t){case"button":case"input":case"select":case"textarea":r=!!r.autoFocus;break e;case"img":r=!0;break e;default:r=!1}}r&&(n.flags|=4)}n.ref!==null&&(n.flags|=512,n.flags|=2097152)}return se(n),null;case 6:if(e&&n.stateNode!=null)oc(e,n,e.memoizedProps,r);else{if(typeof r!="string"&&n.stateNode===null)throw Error(E(166));if(t=Ln(nr.current),Ln(Ke.current),kr(n)){if(r=n.stateNode,t=n.memoizedProps,r[Ge]=n,(i=r.nodeValue!==t)&&(e=ke,e!==null))switch(e.tag){case 3:wr(r.nodeValue,t,(e.mode&1)!==0);break;case 5:e.memoizedProps.suppressHydrationWarning!==!0&&wr(r.nodeValue,t,(e.mode&1)!==0)}i&&(n.flags|=4)}else r=(t.nodeType===9?t:t.ownerDocument).createTextNode(r),r[Ge]=n,n.stateNode=r}return se(n),null;case 13:if(B(q),r=n.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if($&&we!==null&&n.mode&1&&!(n.flags&128))ku(),mt(),n.flags|=98560,i=!1;else if(i=kr(n),r!==null&&r.dehydrated!==null){if(e===null){if(!i)throw Error(E(318));if(i=n.memoizedState,i=i!==null?i.dehydrated:null,!i)throw Error(E(317));i[Ge]=n}else mt(),!(n.flags&128)&&(n.memoizedState=null),n.flags|=4;se(n),i=!1}else De!==null&&(Zi(De),De=null),i=!0;if(!i)return n.flags&65536?n:null}return n.flags&128?(n.lanes=t,n):(r=r!==null,r!==(e!==null&&e.memoizedState!==null)&&r&&(n.child.flags|=8192,n.mode&1&&(e===null||q.current&1?J===0&&(J=3):Ua())),n.updateQueue!==null&&(n.flags|=4),se(n),null);case 4:return gt(),Hi(e,n),e===null&&Zt(n.stateNode.containerInfo),se(n),null;case 10:return Ea(n.type._context),se(n),null;case 17:return _e(n.type)&&Yr(),se(n),null;case 19:if(B(q),i=n.memoizedState,i===null)return se(n),null;if(r=(n.flags&128)!==0,a=i.rendering,a===null)if(r)Rt(i,!1);else{if(J!==0||e!==null&&e.flags&128)for(e=n.child;e!==null;){if(a=to(e),a!==null){for(n.flags|=128,Rt(i,!1),r=a.updateQueue,r!==null&&(n.updateQueue=r,n.flags|=4),n.subtreeFlags=0,r=t,t=n.child;t!==null;)i=t,e=r,i.flags&=14680066,a=i.alternate,a===null?(i.childLanes=0,i.lanes=e,i.child=null,i.subtreeFlags=0,i.memoizedProps=null,i.memoizedState=null,i.updateQueue=null,i.dependencies=null,i.stateNode=null):(i.childLanes=a.childLanes,i.lanes=a.lanes,i.child=a.child,i.subtreeFlags=0,i.deletions=null,i.memoizedProps=a.memoizedProps,i.memoizedState=a.memoizedState,i.updateQueue=a.updateQueue,i.type=a.type,e=a.dependencies,i.dependencies=e===null?null:{lanes:e.lanes,firstContext:e.firstContext}),t=t.sibling;return D(q,q.current&1|2),n.child}e=e.sibling}i.tail!==null&&Y()>ht&&(n.flags|=128,r=!0,Rt(i,!1),n.lanes=4194304)}else{if(!r)if(e=to(a),e!==null){if(n.flags|=128,r=!0,t=e.updateQueue,t!==null&&(n.updateQueue=t,n.flags|=4),Rt(i,!0),i.tail===null&&i.tailMode==="hidden"&&!a.alternate&&!$)return se(n),null}else 2*Y()-i.renderingStartTime>ht&&t!==1073741824&&(n.flags|=128,r=!0,Rt(i,!1),n.lanes=4194304);i.isBackwards?(a.sibling=n.child,n.child=a):(t=i.last,t!==null?t.sibling=a:n.child=a,i.last=a)}return i.tail!==null?(n=i.tail,i.rendering=n,i.tail=n.sibling,i.renderingStartTime=Y(),n.sibling=null,t=q.current,D(q,r?t&1|2:t&1),n):(se(n),null);case 22:case 23:return za(),r=n.memoizedState!==null,e!==null&&e.memoizedState!==null!==r&&(n.flags|=8192),r&&n.mode&1?xe&1073741824&&(se(n),n.subtreeFlags&6&&(n.flags|=8192)):se(n),null;case 24:return null;case 25:return null}throw Error(E(156,n.tag))}function Bd(e,n){switch(va(n),n.tag){case 1:return _e(n.type)&&Yr(),e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 3:return gt(),B(ge),B(ue),Ra(),e=n.flags,e&65536&&!(e&128)?(n.flags=e&-65537|128,n):null;case 5:return Na(n),null;case 13:if(B(q),e=n.memoizedState,e!==null&&e.dehydrated!==null){if(n.alternate===null)throw Error(E(340));mt()}return e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 19:return B(q),null;case 4:return gt(),null;case 10:return Ea(n.type._context),null;case 22:case 23:return za(),null;case 24:return null;default:return null}}var br=!1,le=!1,$d=typeof WeakSet=="function"?WeakSet:Set,R=null;function ot(e,n){var t=e.ref;if(t!==null)if(typeof t=="function")try{t(null)}catch(r){W(e,n,r)}else t.current=null}function qi(e,n,t){try{t()}catch(r){W(e,n,r)}}var Gs=!1;function Hd(e,n){if(Ni=Vr,e=uu(),_a(e)){if("selectionStart"in e)var t={start:e.selectionStart,end:e.selectionEnd};else e:{t=(t=e.ownerDocument)&&t.defaultView||window;var r=t.getSelection&&t.getSelection();if(r&&r.rangeCount!==0){t=r.anchorNode;var o=r.anchorOffset,i=r.focusNode;r=r.focusOffset;try{t.nodeType,i.nodeType}catch{t=null;break e}var a=0,s=-1,l=-1,p=0,g=0,y=e,_=null;n:for(;;){for(var w;y!==t||o!==0&&y.nodeType!==3||(s=a+o),y!==i||r!==0&&y.nodeType!==3||(l=a+r),y.nodeType===3&&(a+=y.nodeValue.length),(w=y.firstChild)!==null;)_=y,y=w;for(;;){if(y===e)break n;if(_===t&&++p===o&&(s=a),_===i&&++g===r&&(l=a),(w=y.nextSibling)!==null)break;y=_,_=y.parentNode}y=w}t=s===-1||l===-1?null:{start:s,end:l}}else t=null}t=t||{start:0,end:0}}else t=null;for(Ri={focusedElem:e,selectionRange:t},Vr=!1,R=n;R!==null;)if(n=R,e=n.child,(n.subtreeFlags&1028)!==0&&e!==null)e.return=n,R=e;else for(;R!==null;){n=R;try{var f=n.alternate;if(n.flags&1024)switch(n.tag){case 0:case 11:case 15:break;case 1:if(f!==null){var m=f.memoizedProps,h=f.memoizedState,c=n.stateNode,u=c.getSnapshotBeforeUpdate(n.elementType===n.type?m:Le(n.type,m),h);c.__reactInternalSnapshotBeforeUpdate=u}break;case 3:var d=n.stateNode.containerInfo;d.nodeType===1?d.textContent="":d.nodeType===9&&d.documentElement&&d.removeChild(d.documentElement);break;case 5:case 6:case 4:case 17:break;default:throw Error(E(163))}}catch(v){W(n,n.return,v)}if(e=n.sibling,e!==null){e.return=n.return,R=e;break}R=n.return}return f=Gs,Gs=!1,f}function Ut(e,n,t){var r=n.updateQueue;if(r=r!==null?r.lastEffect:null,r!==null){var o=r=r.next;do{if((o.tag&e)===e){var i=o.destroy;o.destroy=void 0,i!==void 0&&qi(n,t,i)}o=o.next}while(o!==r)}}function Eo(e,n){if(n=n.updateQueue,n=n!==null?n.lastEffect:null,n!==null){var t=n=n.next;do{if((t.tag&e)===e){var r=t.create;t.destroy=r()}t=t.next}while(t!==n)}}function Vi(e){var n=e.ref;if(n!==null){var t=e.stateNode;switch(e.tag){case 5:e=t;break;default:e=t}typeof n=="function"?n(e):n.current=e}}function ic(e){var n=e.alternate;n!==null&&(e.alternate=null,ic(n)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(n=e.stateNode,n!==null&&(delete n[Ge],delete n[Jt],delete n[Pi],delete n[bd],delete n[Cd])),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}function ac(e){return e.tag===5||e.tag===3||e.tag===4}function Ws(e){e:for(;;){for(;e.sibling===null;){if(e.return===null||ac(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.flags&2||e.child===null||e.tag===4)continue e;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function Gi(e,n,t){var r=e.tag;if(r===5||r===6)e=e.stateNode,n?t.nodeType===8?t.parentNode.insertBefore(e,n):t.insertBefore(e,n):(t.nodeType===8?(n=t.parentNode,n.insertBefore(e,t)):(n=t,n.appendChild(e)),t=t._reactRootContainer,t!=null||n.onclick!==null||(n.onclick=Kr));else if(r!==4&&(e=e.child,e!==null))for(Gi(e,n,t),e=e.sibling;e!==null;)Gi(e,n,t),e=e.sibling}function Wi(e,n,t){var r=e.tag;if(r===5||r===6)e=e.stateNode,n?t.insertBefore(e,n):t.appendChild(e);else if(r!==4&&(e=e.child,e!==null))for(Wi(e,n,t),e=e.sibling;e!==null;)Wi(e,n,t),e=e.sibling}var te=null,je=!1;function pn(e,n,t){for(t=t.child;t!==null;)sc(e,n,t),t=t.sibling}function sc(e,n,t){if(We&&typeof We.onCommitFiberUnmount=="function")try{We.onCommitFiberUnmount(yo,t)}catch{}switch(t.tag){case 5:le||ot(t,n);case 6:var r=te,o=je;te=null,pn(e,n,t),te=r,je=o,te!==null&&(je?(e=te,t=t.stateNode,e.nodeType===8?e.parentNode.removeChild(t):e.removeChild(t)):te.removeChild(t.stateNode));break;case 18:te!==null&&(je?(e=te,t=t.stateNode,e.nodeType===8?Yo(e.parentNode,t):e.nodeType===1&&Yo(e,t),Kt(e)):Yo(te,t.stateNode));break;case 4:r=te,o=je,te=t.stateNode.containerInfo,je=!0,pn(e,n,t),te=r,je=o;break;case 0:case 11:case 14:case 15:if(!le&&(r=t.updateQueue,r!==null&&(r=r.lastEffect,r!==null))){o=r=r.next;do{var i=o,a=i.destroy;i=i.tag,a!==void 0&&(i&2||i&4)&&qi(t,n,a),o=o.next}while(o!==r)}pn(e,n,t);break;case 1:if(!le&&(ot(t,n),r=t.stateNode,typeof r.componentWillUnmount=="function"))try{r.props=t.memoizedProps,r.state=t.memoizedState,r.componentWillUnmount()}catch(s){W(t,n,s)}pn(e,n,t);break;case 21:pn(e,n,t);break;case 22:t.mode&1?(le=(r=le)||t.memoizedState!==null,pn(e,n,t),le=r):pn(e,n,t);break;default:pn(e,n,t)}}function Ks(e){var n=e.updateQueue;if(n!==null){e.updateQueue=null;var t=e.stateNode;t===null&&(t=e.stateNode=new $d),n.forEach(function(r){var o=Xd.bind(null,e,r);t.has(r)||(t.add(r),r.then(o,o))})}}function Me(e,n){var t=n.deletions;if(t!==null)for(var r=0;r<t.length;r++){var o=t[r];try{var i=e,a=n,s=a;e:for(;s!==null;){switch(s.tag){case 5:te=s.stateNode,je=!1;break e;case 3:te=s.stateNode.containerInfo,je=!0;break e;case 4:te=s.stateNode.containerInfo,je=!0;break e}s=s.return}if(te===null)throw Error(E(160));sc(i,a,o),te=null,je=!1;var l=o.alternate;l!==null&&(l.return=null),o.return=null}catch(p){W(o,n,p)}}if(n.subtreeFlags&12854)for(n=n.child;n!==null;)lc(n,e),n=n.sibling}function lc(e,n){var t=e.alternate,r=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:if(Me(n,e),qe(e),r&4){try{Ut(3,e,e.return),Eo(3,e)}catch(m){W(e,e.return,m)}try{Ut(5,e,e.return)}catch(m){W(e,e.return,m)}}break;case 1:Me(n,e),qe(e),r&512&&t!==null&&ot(t,t.return);break;case 5:if(Me(n,e),qe(e),r&512&&t!==null&&ot(t,t.return),e.flags&32){var o=e.stateNode;try{qt(o,"")}catch(m){W(e,e.return,m)}}if(r&4&&(o=e.stateNode,o!=null)){var i=e.memoizedProps,a=t!==null?t.memoizedProps:i,s=e.type,l=e.updateQueue;if(e.updateQueue=null,l!==null)try{s==="input"&&i.type==="radio"&&i.name!=null&&Al(o,i),_i(s,a);var p=_i(s,i);for(a=0;a<l.length;a+=2){var g=l[a],y=l[a+1];g==="style"?Ml(o,y):g==="dangerouslySetInnerHTML"?Fl(o,y):g==="children"?qt(o,y):oa(o,g,y,p)}switch(s){case"input":di(o,i);break;case"textarea":Pl(o,i);break;case"select":var _=o._wrapperState.wasMultiple;o._wrapperState.wasMultiple=!!i.multiple;var w=i.value;w!=null?at(o,!!i.multiple,w,!1):_!==!!i.multiple&&(i.defaultValue!=null?at(o,!!i.multiple,i.defaultValue,!0):at(o,!!i.multiple,i.multiple?[]:"",!1))}o[Jt]=i}catch(m){W(e,e.return,m)}}break;case 6:if(Me(n,e),qe(e),r&4){if(e.stateNode===null)throw Error(E(162));o=e.stateNode,i=e.memoizedProps;try{o.nodeValue=i}catch(m){W(e,e.return,m)}}break;case 3:if(Me(n,e),qe(e),r&4&&t!==null&&t.memoizedState.isDehydrated)try{Kt(n.containerInfo)}catch(m){W(e,e.return,m)}break;case 4:Me(n,e),qe(e);break;case 13:Me(n,e),qe(e),o=e.child,o.flags&8192&&(i=o.memoizedState!==null,o.stateNode.isHidden=i,!i||o.alternate!==null&&o.alternate.memoizedState!==null||(ja=Y())),r&4&&Ks(e);break;case 22:if(g=t!==null&&t.memoizedState!==null,e.mode&1?(le=(p=le)||g,Me(n,e),le=p):Me(n,e),qe(e),r&8192){if(p=e.memoizedState!==null,(e.stateNode.isHidden=p)&&!g&&e.mode&1)for(R=e,g=e.child;g!==null;){for(y=R=g;R!==null;){switch(_=R,w=_.child,_.tag){case 0:case 11:case 14:case 15:Ut(4,_,_.return);break;case 1:ot(_,_.return);var f=_.stateNode;if(typeof f.componentWillUnmount=="function"){r=_,t=_.return;try{n=r,f.props=n.memoizedProps,f.state=n.memoizedState,f.componentWillUnmount()}catch(m){W(r,t,m)}}break;case 5:ot(_,_.return);break;case 22:if(_.memoizedState!==null){Qs(y);continue}}w!==null?(w.return=_,R=w):Qs(y)}g=g.sibling}e:for(g=null,y=e;;){if(y.tag===5){if(g===null){g=y;try{o=y.stateNode,p?(i=o.style,typeof i.setProperty=="function"?i.setProperty("display","none","important"):i.display="none"):(s=y.stateNode,l=y.memoizedProps.style,a=l!=null&&l.hasOwnProperty("display")?l.display:null,s.style.display=Ol("display",a))}catch(m){W(e,e.return,m)}}}else if(y.tag===6){if(g===null)try{y.stateNode.nodeValue=p?"":y.memoizedProps}catch(m){W(e,e.return,m)}}else if((y.tag!==22&&y.tag!==23||y.memoizedState===null||y===e)&&y.child!==null){y.child.return=y,y=y.child;continue}if(y===e)break e;for(;y.sibling===null;){if(y.return===null||y.return===e)break e;g===y&&(g=null),y=y.return}g===y&&(g=null),y.sibling.return=y.return,y=y.sibling}}break;case 19:Me(n,e),qe(e),r&4&&Ks(e);break;case 21:break;default:Me(n,e),qe(e)}}function qe(e){var n=e.flags;if(n&2){try{e:{for(var t=e.return;t!==null;){if(ac(t)){var r=t;break e}t=t.return}throw Error(E(160))}switch(r.tag){case 5:var o=r.stateNode;r.flags&32&&(qt(o,""),r.flags&=-33);var i=Ws(e);Wi(e,i,o);break;case 3:case 4:var a=r.stateNode.containerInfo,s=Ws(e);Gi(e,s,a);break;default:throw Error(E(161))}}catch(l){W(e,e.return,l)}e.flags&=-3}n&4096&&(e.flags&=-4097)}function qd(e,n,t){R=e,uc(e)}function uc(e,n,t){for(var r=(e.mode&1)!==0;R!==null;){var o=R,i=o.child;if(o.tag===22&&r){var a=o.memoizedState!==null||br;if(!a){var s=o.alternate,l=s!==null&&s.memoizedState!==null||le;s=br;var p=le;if(br=a,(le=l)&&!p)for(R=o;R!==null;)a=R,l=a.child,a.tag===22&&a.memoizedState!==null?Zs(o):l!==null?(l.return=a,R=l):Zs(o);for(;i!==null;)R=i,uc(i),i=i.sibling;R=o,br=s,le=p}Ys(e)}else o.subtreeFlags&8772&&i!==null?(i.return=o,R=i):Ys(e)}}function Ys(e){for(;R!==null;){var n=R;if(n.flags&8772){var t=n.alternate;try{if(n.flags&8772)switch(n.tag){case 0:case 11:case 15:le||Eo(5,n);break;case 1:var r=n.stateNode;if(n.flags&4&&!le)if(t===null)r.componentDidMount();else{var o=n.elementType===n.type?t.memoizedProps:Le(n.type,t.memoizedProps);r.componentDidUpdate(o,t.memoizedState,r.__reactInternalSnapshotBeforeUpdate)}var i=n.updateQueue;i!==null&&Fs(n,i,r);break;case 3:var a=n.updateQueue;if(a!==null){if(t=null,n.child!==null)switch(n.child.tag){case 5:t=n.child.stateNode;break;case 1:t=n.child.stateNode}Fs(n,a,t)}break;case 5:var s=n.stateNode;if(t===null&&n.flags&4){t=s;var l=n.memoizedProps;switch(n.type){case"button":case"input":case"select":case"textarea":l.autoFocus&&t.focus();break;case"img":l.src&&(t.src=l.src)}}break;case 6:break;case 4:break;case 12:break;case 13:if(n.memoizedState===null){var p=n.alternate;if(p!==null){var g=p.memoizedState;if(g!==null){var y=g.dehydrated;y!==null&&Kt(y)}}}break;case 19:case 17:case 21:case 22:case 23:case 25:break;default:throw Error(E(163))}le||n.flags&512&&Vi(n)}catch(_){W(n,n.return,_)}}if(n===e){R=null;break}if(t=n.sibling,t!==null){t.return=n.return,R=t;break}R=n.return}}function Qs(e){for(;R!==null;){var n=R;if(n===e){R=null;break}var t=n.sibling;if(t!==null){t.return=n.return,R=t;break}R=n.return}}function Zs(e){for(;R!==null;){var n=R;try{switch(n.tag){case 0:case 11:case 15:var t=n.return;try{Eo(4,n)}catch(l){W(n,t,l)}break;case 1:var r=n.stateNode;if(typeof r.componentDidMount=="function"){var o=n.return;try{r.componentDidMount()}catch(l){W(n,o,l)}}var i=n.return;try{Vi(n)}catch(l){W(n,i,l)}break;case 5:var a=n.return;try{Vi(n)}catch(l){W(n,a,l)}}}catch(l){W(n,n.return,l)}if(n===e){R=null;break}var s=n.sibling;if(s!==null){s.return=n.return,R=s;break}R=n.return}}var Vd=Math.ceil,io=ln.ReactCurrentDispatcher,Ma=ln.ReactCurrentOwner,Ae=ln.ReactCurrentBatchConfig,M=0,ne=null,Q=null,re=0,xe=0,it=An(0),J=0,ir=null,$n=0,So=0,La=0,Bt=null,me=null,ja=0,ht=1/0,Xe=null,ao=!1,Ki=null,Sn=null,Cr=!1,_n=null,so=0,$t=0,Yi=null,jr=-1,Dr=0;function pe(){return M&6?Y():jr!==-1?jr:jr=Y()}function bn(e){return e.mode&1?M&2&&re!==0?re&-re:Rd.transition!==null?(Dr===0&&(Dr=Wl()),Dr):(e=L,e!==0||(e=window.event,e=e===void 0?16:eu(e.type)),e):1}function Be(e,n,t,r){if(50<$t)throw $t=0,Yi=null,Error(E(185));sr(e,t,r),(!(M&2)||e!==ne)&&(e===ne&&(!(M&2)&&(So|=t),J===4&&yn(e,re)),he(e,r),t===1&&M===0&&!(n.mode&1)&&(ht=Y()+500,xo&&Pn()))}function he(e,n){var t=e.callbackNode;Rp(e,n);var r=qr(e,e===ne?re:0);if(r===0)t!==null&&as(t),e.callbackNode=null,e.callbackPriority=0;else if(n=r&-r,e.callbackPriority!==n){if(t!=null&&as(t),n===1)e.tag===0?Nd(Xs.bind(null,e)):vu(Xs.bind(null,e)),Ed(function(){!(M&6)&&Pn()}),t=null;else{switch(Kl(r)){case 1:t=ua;break;case 4:t=Vl;break;case 16:t=Hr;break;case 536870912:t=Gl;break;default:t=Hr}t=_c(t,cc.bind(null,e))}e.callbackPriority=n,e.callbackNode=t}}function cc(e,n){if(jr=-1,Dr=0,M&6)throw Error(E(327));var t=e.callbackNode;if(pt()&&e.callbackNode!==t)return null;var r=qr(e,e===ne?re:0);if(r===0)return null;if(r&30||r&e.expiredLanes||n)n=lo(e,r);else{n=r;var o=M;M|=2;var i=dc();(ne!==e||re!==n)&&(Xe=null,ht=Y()+500,jn(e,n));do try{Kd();break}catch(s){pc(e,s)}while(!0);ka(),io.current=i,M=o,Q!==null?n=0:(ne=null,re=0,n=J)}if(n!==0){if(n===2&&(o=ki(e),o!==0&&(r=o,n=Qi(e,o))),n===1)throw t=ir,jn(e,0),yn(e,r),he(e,Y()),t;if(n===6)yn(e,r);else{if(o=e.current.alternate,!(r&30)&&!Gd(o)&&(n=lo(e,r),n===2&&(i=ki(e),i!==0&&(r=i,n=Qi(e,i))),n===1))throw t=ir,jn(e,0),yn(e,r),he(e,Y()),t;switch(e.finishedWork=o,e.finishedLanes=r,n){case 0:case 1:throw Error(E(345));case 2:Fn(e,me,Xe);break;case 3:if(yn(e,r),(r&130023424)===r&&(n=ja+500-Y(),10<n)){if(qr(e,0)!==0)break;if(o=e.suspendedLanes,(o&r)!==r){pe(),e.pingedLanes|=e.suspendedLanes&o;break}e.timeoutHandle=Ai(Fn.bind(null,e,me,Xe),n);break}Fn(e,me,Xe);break;case 4:if(yn(e,r),(r&4194240)===r)break;for(n=e.eventTimes,o=-1;0<r;){var a=31-Ue(r);i=1<<a,a=n[a],a>o&&(o=a),r&=~i}if(r=o,r=Y()-r,r=(120>r?120:480>r?480:1080>r?1080:1920>r?1920:3e3>r?3e3:4320>r?4320:1960*Vd(r/1960))-r,10<r){e.timeoutHandle=Ai(Fn.bind(null,e,me,Xe),r);break}Fn(e,me,Xe);break;case 5:Fn(e,me,Xe);break;default:throw Error(E(329))}}}return he(e,Y()),e.callbackNode===t?cc.bind(null,e):null}function Qi(e,n){var t=Bt;return e.current.memoizedState.isDehydrated&&(jn(e,n).flags|=256),e=lo(e,n),e!==2&&(n=me,me=t,n!==null&&Zi(n)),e}function Zi(e){me===null?me=e:me.push.apply(me,e)}function Gd(e){for(var n=e;;){if(n.flags&16384){var t=n.updateQueue;if(t!==null&&(t=t.stores,t!==null))for(var r=0;r<t.length;r++){var o=t[r],i=o.getSnapshot;o=o.value;try{if(!$e(i(),o))return!1}catch{return!1}}}if(t=n.child,n.subtreeFlags&16384&&t!==null)t.return=n,n=t;else{if(n===e)break;for(;n.sibling===null;){if(n.return===null||n.return===e)return!0;n=n.return}n.sibling.return=n.return,n=n.sibling}}return!0}function yn(e,n){for(n&=~La,n&=~So,e.suspendedLanes|=n,e.pingedLanes&=~n,e=e.expirationTimes;0<n;){var t=31-Ue(n),r=1<<t;e[t]=-1,n&=~r}}function Xs(e){if(M&6)throw Error(E(327));pt();var n=qr(e,0);if(!(n&1))return he(e,Y()),null;var t=lo(e,n);if(e.tag!==0&&t===2){var r=ki(e);r!==0&&(n=r,t=Qi(e,r))}if(t===1)throw t=ir,jn(e,0),yn(e,n),he(e,Y()),t;if(t===6)throw Error(E(345));return e.finishedWork=e.current.alternate,e.finishedLanes=n,Fn(e,me,Xe),he(e,Y()),null}function Da(e,n){var t=M;M|=1;try{return e(n)}finally{M=t,M===0&&(ht=Y()+500,xo&&Pn())}}function Hn(e){_n!==null&&_n.tag===0&&!(M&6)&&pt();var n=M;M|=1;var t=Ae.transition,r=L;try{if(Ae.transition=null,L=1,e)return e()}finally{L=r,Ae.transition=t,M=n,!(M&6)&&Pn()}}function za(){xe=it.current,B(it)}function jn(e,n){e.finishedWork=null,e.finishedLanes=0;var t=e.timeoutHandle;if(t!==-1&&(e.timeoutHandle=-1,kd(t)),Q!==null)for(t=Q.return;t!==null;){var r=t;switch(va(r),r.tag){case 1:r=r.type.childContextTypes,r!=null&&Yr();break;case 3:gt(),B(ge),B(ue),Ra();break;case 5:Na(r);break;case 4:gt();break;case 13:B(q);break;case 19:B(q);break;case 10:Ea(r.type._context);break;case 22:case 23:za()}t=t.return}if(ne=e,Q=e=Cn(e.current,null),re=xe=n,J=0,ir=null,La=So=$n=0,me=Bt=null,Mn!==null){for(n=0;n<Mn.length;n++)if(t=Mn[n],r=t.interleaved,r!==null){t.interleaved=null;var o=r.next,i=t.pending;if(i!==null){var a=i.next;i.next=o,r.next=a}t.pending=r}Mn=null}return e}function pc(e,n){do{var t=Q;try{if(ka(),Or.current=oo,ro){for(var r=V.memoizedState;r!==null;){var o=r.queue;o!==null&&(o.pending=null),r=r.next}ro=!1}if(Bn=0,ee=X=V=null,zt=!1,tr=0,Ma.current=null,t===null||t.return===null){J=1,ir=n,Q=null;break}e:{var i=e,a=t.return,s=t,l=n;if(n=re,s.flags|=32768,l!==null&&typeof l=="object"&&typeof l.then=="function"){var p=l,g=s,y=g.tag;if(!(g.mode&1)&&(y===0||y===11||y===15)){var _=g.alternate;_?(g.updateQueue=_.updateQueue,g.memoizedState=_.memoizedState,g.lanes=_.lanes):(g.updateQueue=null,g.memoizedState=null)}var w=zs(a);if(w!==null){w.flags&=-257,Us(w,a,s,i,n),w.mode&1&&Ds(i,p,n),n=w,l=p;var f=n.updateQueue;if(f===null){var m=new Set;m.add(l),n.updateQueue=m}else f.add(l);break e}else{if(!(n&1)){Ds(i,p,n),Ua();break e}l=Error(E(426))}}else if($&&s.mode&1){var h=zs(a);if(h!==null){!(h.flags&65536)&&(h.flags|=256),Us(h,a,s,i,n),xa(_t(l,s));break e}}i=l=_t(l,s),J!==4&&(J=2),Bt===null?Bt=[i]:Bt.push(i),i=a;do{switch(i.tag){case 3:i.flags|=65536,n&=-n,i.lanes|=n;var c=Ku(i,l,n);Is(i,c);break e;case 1:s=l;var u=i.type,d=i.stateNode;if(!(i.flags&128)&&(typeof u.getDerivedStateFromError=="function"||d!==null&&typeof d.componentDidCatch=="function"&&(Sn===null||!Sn.has(d)))){i.flags|=65536,n&=-n,i.lanes|=n;var v=Yu(i,s,n);Is(i,v);break e}}i=i.return}while(i!==null)}mc(t)}catch(k){n=k,Q===t&&t!==null&&(Q=t=t.return);continue}break}while(!0)}function dc(){var e=io.current;return io.current=oo,e===null?oo:e}function Ua(){(J===0||J===3||J===2)&&(J=4),ne===null||!($n&268435455)&&!(So&268435455)||yn(ne,re)}function lo(e,n){var t=M;M|=2;var r=dc();(ne!==e||re!==n)&&(Xe=null,jn(e,n));do try{Wd();break}catch(o){pc(e,o)}while(!0);if(ka(),M=t,io.current=r,Q!==null)throw Error(E(261));return ne=null,re=0,J}function Wd(){for(;Q!==null;)fc(Q)}function Kd(){for(;Q!==null&&!vp();)fc(Q)}function fc(e){var n=gc(e.alternate,e,xe);e.memoizedProps=e.pendingProps,n===null?mc(e):Q=n,Ma.current=null}function mc(e){var n=e;do{var t=n.alternate;if(e=n.return,n.flags&32768){if(t=Bd(t,n),t!==null){t.flags&=32767,Q=t;return}if(e!==null)e.flags|=32768,e.subtreeFlags=0,e.deletions=null;else{J=6,Q=null;return}}else if(t=Ud(t,n,xe),t!==null){Q=t;return}if(n=n.sibling,n!==null){Q=n;return}Q=n=e}while(n!==null);J===0&&(J=5)}function Fn(e,n,t){var r=L,o=Ae.transition;try{Ae.transition=null,L=1,Yd(e,n,t,r)}finally{Ae.transition=o,L=r}return null}function Yd(e,n,t,r){do pt();while(_n!==null);if(M&6)throw Error(E(327));t=e.finishedWork;var o=e.finishedLanes;if(t===null)return null;if(e.finishedWork=null,e.finishedLanes=0,t===e.current)throw Error(E(177));e.callbackNode=null,e.callbackPriority=0;var i=t.lanes|t.childLanes;if(Tp(e,i),e===ne&&(Q=ne=null,re=0),!(t.subtreeFlags&2064)&&!(t.flags&2064)||Cr||(Cr=!0,_c(Hr,function(){return pt(),null})),i=(t.flags&15990)!==0,t.subtreeFlags&15990||i){i=Ae.transition,Ae.transition=null;var a=L;L=1;var s=M;M|=4,Ma.current=null,Hd(e,t),lc(t,e),yd(Ri),Vr=!!Ni,Ri=Ni=null,e.current=t,qd(t),xp(),M=s,L=a,Ae.transition=i}else e.current=t;if(Cr&&(Cr=!1,_n=e,so=o),i=e.pendingLanes,i===0&&(Sn=null),Ep(t.stateNode),he(e,Y()),n!==null)for(r=e.onRecoverableError,t=0;t<n.length;t++)o=n[t],r(o.value,{componentStack:o.stack,digest:o.digest});if(ao)throw ao=!1,e=Ki,Ki=null,e;return so&1&&e.tag!==0&&pt(),i=e.pendingLanes,i&1?e===Yi?$t++:($t=0,Yi=e):$t=0,Pn(),null}function pt(){if(_n!==null){var e=Kl(so),n=Ae.transition,t=L;try{if(Ae.transition=null,L=16>e?16:e,_n===null)var r=!1;else{if(e=_n,_n=null,so=0,M&6)throw Error(E(331));var o=M;for(M|=4,R=e.current;R!==null;){var i=R,a=i.child;if(R.flags&16){var s=i.deletions;if(s!==null){for(var l=0;l<s.length;l++){var p=s[l];for(R=p;R!==null;){var g=R;switch(g.tag){case 0:case 11:case 15:Ut(8,g,i)}var y=g.child;if(y!==null)y.return=g,R=y;else for(;R!==null;){g=R;var _=g.sibling,w=g.return;if(ic(g),g===p){R=null;break}if(_!==null){_.return=w,R=_;break}R=w}}}var f=i.alternate;if(f!==null){var m=f.child;if(m!==null){f.child=null;do{var h=m.sibling;m.sibling=null,m=h}while(m!==null)}}R=i}}if(i.subtreeFlags&2064&&a!==null)a.return=i,R=a;else e:for(;R!==null;){if(i=R,i.flags&2048)switch(i.tag){case 0:case 11:case 15:Ut(9,i,i.return)}var c=i.sibling;if(c!==null){c.return=i.return,R=c;break e}R=i.return}}var u=e.current;for(R=u;R!==null;){a=R;var d=a.child;if(a.subtreeFlags&2064&&d!==null)d.return=a,R=d;else e:for(a=u;R!==null;){if(s=R,s.flags&2048)try{switch(s.tag){case 0:case 11:case 15:Eo(9,s)}}catch(k){W(s,s.return,k)}if(s===a){R=null;break e}var v=s.sibling;if(v!==null){v.return=s.return,R=v;break e}R=s.return}}if(M=o,Pn(),We&&typeof We.onPostCommitFiberRoot=="function")try{We.onPostCommitFiberRoot(yo,e)}catch{}r=!0}return r}finally{L=t,Ae.transition=n}}return!1}function Js(e,n,t){n=_t(t,n),n=Ku(e,n,1),e=En(e,n,1),n=pe(),e!==null&&(sr(e,1,n),he(e,n))}function W(e,n,t){if(e.tag===3)Js(e,e,t);else for(;n!==null;){if(n.tag===3){Js(n,e,t);break}else if(n.tag===1){var r=n.stateNode;if(typeof n.type.getDerivedStateFromError=="function"||typeof r.componentDidCatch=="function"&&(Sn===null||!Sn.has(r))){e=_t(t,e),e=Yu(n,e,1),n=En(n,e,1),e=pe(),n!==null&&(sr(n,1,e),he(n,e));break}}n=n.return}}function Qd(e,n,t){var r=e.pingCache;r!==null&&r.delete(n),n=pe(),e.pingedLanes|=e.suspendedLanes&t,ne===e&&(re&t)===t&&(J===4||J===3&&(re&130023424)===re&&500>Y()-ja?jn(e,0):La|=t),he(e,n)}function yc(e,n){n===0&&(e.mode&1?(n=gr,gr<<=1,!(gr&130023424)&&(gr=4194304)):n=1);var t=pe();e=an(e,n),e!==null&&(sr(e,n,t),he(e,t))}function Zd(e){var n=e.memoizedState,t=0;n!==null&&(t=n.retryLane),yc(e,t)}function Xd(e,n){var t=0;switch(e.tag){case 13:var r=e.stateNode,o=e.memoizedState;o!==null&&(t=o.retryLane);break;case 19:r=e.stateNode;break;default:throw Error(E(314))}r!==null&&r.delete(n),yc(e,t)}var gc;gc=function(e,n,t){if(e!==null)if(e.memoizedProps!==n.pendingProps||ge.current)ye=!0;else{if(!(e.lanes&t)&&!(n.flags&128))return ye=!1,zd(e,n,t);ye=!!(e.flags&131072)}else ye=!1,$&&n.flags&1048576&&xu(n,Xr,n.index);switch(n.lanes=0,n.tag){case 2:var r=n.type;Lr(e,n),e=n.pendingProps;var o=ft(n,ue.current);ct(n,t),o=Aa(null,n,r,e,o,t);var i=Pa();return n.flags|=1,typeof o=="object"&&o!==null&&typeof o.render=="function"&&o.$$typeof===void 0?(n.tag=1,n.memoizedState=null,n.updateQueue=null,_e(r)?(i=!0,Qr(n)):i=!1,n.memoizedState=o.state!==null&&o.state!==void 0?o.state:null,ba(n),o.updater=ko,n.stateNode=o,o._reactInternals=n,ji(n,r,e,t),n=Ui(null,n,r,!0,i,t)):(n.tag=0,$&&i&&ha(n),ce(null,n,o,t),n=n.child),n;case 16:r=n.elementType;e:{switch(Lr(e,n),e=n.pendingProps,o=r._init,r=o(r._payload),n.type=r,o=n.tag=ef(r),e=Le(r,e),o){case 0:n=zi(null,n,r,e,t);break e;case 1:n=Hs(null,n,r,e,t);break e;case 11:n=Bs(null,n,r,e,t);break e;case 14:n=$s(null,n,r,Le(r.type,e),t);break e}throw Error(E(306,r,""))}return n;case 0:return r=n.type,o=n.pendingProps,o=n.elementType===r?o:Le(r,o),zi(e,n,r,o,t);case 1:return r=n.type,o=n.pendingProps,o=n.elementType===r?o:Le(r,o),Hs(e,n,r,o,t);case 3:e:{if(Ju(n),e===null)throw Error(E(387));r=n.pendingProps,i=n.memoizedState,o=i.element,Cu(e,n),no(n,r,null,t);var a=n.memoizedState;if(r=a.element,i.isDehydrated)if(i={element:r,isDehydrated:!1,cache:a.cache,pendingSuspenseBoundaries:a.pendingSuspenseBoundaries,transitions:a.transitions},n.updateQueue.baseState=i,n.memoizedState=i,n.flags&256){o=_t(Error(E(423)),n),n=qs(e,n,r,t,o);break e}else if(r!==o){o=_t(Error(E(424)),n),n=qs(e,n,r,t,o);break e}else for(we=kn(n.stateNode.containerInfo.firstChild),ke=n,$=!0,De=null,t=Su(n,null,r,t),n.child=t;t;)t.flags=t.flags&-3|4096,t=t.sibling;else{if(mt(),r===o){n=sn(e,n,t);break e}ce(e,n,r,t)}n=n.child}return n;case 5:return Nu(n),e===null&&Oi(n),r=n.type,o=n.pendingProps,i=e!==null?e.memoizedProps:null,a=o.children,Ti(r,o)?a=null:i!==null&&Ti(r,i)&&(n.flags|=32),Xu(e,n),ce(e,n,a,t),n.child;case 6:return e===null&&Oi(n),null;case 13:return ec(e,n,t);case 4:return Ca(n,n.stateNode.containerInfo),r=n.pendingProps,e===null?n.child=yt(n,null,r,t):ce(e,n,r,t),n.child;case 11:return r=n.type,o=n.pendingProps,o=n.elementType===r?o:Le(r,o),Bs(e,n,r,o,t);case 7:return ce(e,n,n.pendingProps,t),n.child;case 8:return ce(e,n,n.pendingProps.children,t),n.child;case 12:return ce(e,n,n.pendingProps.children,t),n.child;case 10:e:{if(r=n.type._context,o=n.pendingProps,i=n.memoizedProps,a=o.value,D(Jr,r._currentValue),r._currentValue=a,i!==null)if($e(i.value,a)){if(i.children===o.children&&!ge.current){n=sn(e,n,t);break e}}else for(i=n.child,i!==null&&(i.return=n);i!==null;){var s=i.dependencies;if(s!==null){a=i.child;for(var l=s.firstContext;l!==null;){if(l.context===r){if(i.tag===1){l=tn(-1,t&-t),l.tag=2;var p=i.updateQueue;if(p!==null){p=p.shared;var g=p.pending;g===null?l.next=l:(l.next=g.next,g.next=l),p.pending=l}}i.lanes|=t,l=i.alternate,l!==null&&(l.lanes|=t),Mi(i.return,t,n),s.lanes|=t;break}l=l.next}}else if(i.tag===10)a=i.type===n.type?null:i.child;else if(i.tag===18){if(a=i.return,a===null)throw Error(E(341));a.lanes|=t,s=a.alternate,s!==null&&(s.lanes|=t),Mi(a,t,n),a=i.sibling}else a=i.child;if(a!==null)a.return=i;else for(a=i;a!==null;){if(a===n){a=null;break}if(i=a.sibling,i!==null){i.return=a.return,a=i;break}a=a.return}i=a}ce(e,n,o.children,t),n=n.child}return n;case 9:return o=n.type,r=n.pendingProps.children,ct(n,t),o=Pe(o),r=r(o),n.flags|=1,ce(e,n,r,t),n.child;case 14:return r=n.type,o=Le(r,n.pendingProps),o=Le(r.type,o),$s(e,n,r,o,t);case 15:return Qu(e,n,n.type,n.pendingProps,t);case 17:return r=n.type,o=n.pendingProps,o=n.elementType===r?o:Le(r,o),Lr(e,n),n.tag=1,_e(r)?(e=!0,Qr(n)):e=!1,ct(n,t),Wu(n,r,o),ji(n,r,o,t),Ui(null,n,r,!0,e,t);case 19:return nc(e,n,t);case 22:return Zu(e,n,t)}throw Error(E(156,n.tag))};function _c(e,n){return ql(e,n)}function Jd(e,n,t,r){this.tag=e,this.key=t,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.ref=null,this.pendingProps=n,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=r,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function Te(e,n,t,r){return new Jd(e,n,t,r)}function Ba(e){return e=e.prototype,!(!e||!e.isReactComponent)}function ef(e){if(typeof e=="function")return Ba(e)?1:0;if(e!=null){if(e=e.$$typeof,e===aa)return 11;if(e===sa)return 14}return 2}function Cn(e,n){var t=e.alternate;return t===null?(t=Te(e.tag,n,e.key,e.mode),t.elementType=e.elementType,t.type=e.type,t.stateNode=e.stateNode,t.alternate=e,e.alternate=t):(t.pendingProps=n,t.type=e.type,t.flags=0,t.subtreeFlags=0,t.deletions=null),t.flags=e.flags&14680064,t.childLanes=e.childLanes,t.lanes=e.lanes,t.child=e.child,t.memoizedProps=e.memoizedProps,t.memoizedState=e.memoizedState,t.updateQueue=e.updateQueue,n=e.dependencies,t.dependencies=n===null?null:{lanes:n.lanes,firstContext:n.firstContext},t.sibling=e.sibling,t.index=e.index,t.ref=e.ref,t}function zr(e,n,t,r,o,i){var a=2;if(r=e,typeof e=="function")Ba(e)&&(a=1);else if(typeof e=="string")a=5;else e:switch(e){case Yn:return Dn(t.children,o,i,n);case ia:a=8,o|=8;break;case si:return e=Te(12,t,n,o|2),e.elementType=si,e.lanes=i,e;case li:return e=Te(13,t,n,o),e.elementType=li,e.lanes=i,e;case ui:return e=Te(19,t,n,o),e.elementType=ui,e.lanes=i,e;case Nl:return bo(t,o,i,n);default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case bl:a=10;break e;case Cl:a=9;break e;case aa:a=11;break e;case sa:a=14;break e;case dn:a=16,r=null;break e}throw Error(E(130,e==null?e:typeof e,""))}return n=Te(a,t,n,o),n.elementType=e,n.type=r,n.lanes=i,n}function Dn(e,n,t,r){return e=Te(7,e,r,n),e.lanes=t,e}function bo(e,n,t,r){return e=Te(22,e,r,n),e.elementType=Nl,e.lanes=t,e.stateNode={isHidden:!1},e}function ri(e,n,t){return e=Te(6,e,null,n),e.lanes=t,e}function oi(e,n,t){return n=Te(4,e.children!==null?e.children:[],e.key,n),n.lanes=t,n.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},n}function nf(e,n,t,r,o){this.tag=n,this.containerInfo=e,this.finishedWork=this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.pendingContext=this.context=null,this.callbackPriority=0,this.eventTimes=Do(0),this.expirationTimes=Do(-1),this.entangledLanes=this.finishedLanes=this.mutableReadLanes=this.expiredLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=Do(0),this.identifierPrefix=r,this.onRecoverableError=o,this.mutableSourceEagerHydrationData=null}function $a(e,n,t,r,o,i,a,s,l){return e=new nf(e,n,t,s,l),n===1?(n=1,i===!0&&(n|=8)):n=0,i=Te(3,null,null,n),e.current=i,i.stateNode=e,i.memoizedState={element:r,isDehydrated:t,cache:null,transitions:null,pendingSuspenseBoundaries:null},ba(i),e}function tf(e,n,t){var r=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:Kn,key:r==null?null:""+r,children:e,containerInfo:n,implementation:t}}function hc(e){if(!e)return Rn;e=e._reactInternals;e:{if(Vn(e)!==e||e.tag!==1)throw Error(E(170));var n=e;do{switch(n.tag){case 3:n=n.stateNode.context;break e;case 1:if(_e(n.type)){n=n.stateNode.__reactInternalMemoizedMergedChildContext;break e}}n=n.return}while(n!==null);throw Error(E(171))}if(e.tag===1){var t=e.type;if(_e(t))return hu(e,t,n)}return n}function vc(e,n,t,r,o,i,a,s,l){return e=$a(t,r,!0,e,o,i,a,s,l),e.context=hc(null),t=e.current,r=pe(),o=bn(t),i=tn(r,o),i.callback=n??null,En(t,i,o),e.current.lanes=o,sr(e,o,r),he(e,r),e}function Co(e,n,t,r){var o=n.current,i=pe(),a=bn(o);return t=hc(t),n.context===null?n.context=t:n.pendingContext=t,n=tn(i,a),n.payload={element:e},r=r===void 0?null:r,r!==null&&(n.callback=r),e=En(o,n,a),e!==null&&(Be(e,o,a,i),Fr(e,o,a)),a}function uo(e){if(e=e.current,!e.child)return null;switch(e.child.tag){case 5:return e.child.stateNode;default:return e.child.stateNode}}function el(e,n){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var t=e.retryLane;e.retryLane=t!==0&&t<n?t:n}}function Ha(e,n){el(e,n),(e=e.alternate)&&el(e,n)}function rf(){return null}var xc=typeof reportError=="function"?reportError:function(e){console.error(e)};function qa(e){this._internalRoot=e}No.prototype.render=qa.prototype.render=function(e){var n=this._internalRoot;if(n===null)throw Error(E(409));Co(e,n,null,null)};No.prototype.unmount=qa.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var n=e.containerInfo;Hn(function(){Co(null,e,null,null)}),n[on]=null}};function No(e){this._internalRoot=e}No.prototype.unstable_scheduleHydration=function(e){if(e){var n=Zl();e={blockedOn:null,target:e,priority:n};for(var t=0;t<mn.length&&n!==0&&n<mn[t].priority;t++);mn.splice(t,0,e),t===0&&Jl(e)}};function Va(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function Ro(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11&&(e.nodeType!==8||e.nodeValue!==" react-mount-point-unstable "))}function nl(){}function of(e,n,t,r,o){if(o){if(typeof r=="function"){var i=r;r=function(){var p=uo(a);i.call(p)}}var a=vc(n,r,e,0,null,!1,!1,"",nl);return e._reactRootContainer=a,e[on]=a.current,Zt(e.nodeType===8?e.parentNode:e),Hn(),a}for(;o=e.lastChild;)e.removeChild(o);if(typeof r=="function"){var s=r;r=function(){var p=uo(l);s.call(p)}}var l=$a(e,0,!1,null,null,!1,!1,"",nl);return e._reactRootContainer=l,e[on]=l.current,Zt(e.nodeType===8?e.parentNode:e),Hn(function(){Co(n,l,t,r)}),l}function To(e,n,t,r,o){var i=t._reactRootContainer;if(i){var a=i;if(typeof o=="function"){var s=o;o=function(){var l=uo(a);s.call(l)}}Co(n,a,e,o)}else a=of(t,n,e,o,r);return uo(a)}Yl=function(e){switch(e.tag){case 3:var n=e.stateNode;if(n.current.memoizedState.isDehydrated){var t=It(n.pendingLanes);t!==0&&(ca(n,t|1),he(n,Y()),!(M&6)&&(ht=Y()+500,Pn()))}break;case 13:Hn(function(){var r=an(e,1);if(r!==null){var o=pe();Be(r,e,1,o)}}),Ha(e,1)}};pa=function(e){if(e.tag===13){var n=an(e,134217728);if(n!==null){var t=pe();Be(n,e,134217728,t)}Ha(e,134217728)}};Ql=function(e){if(e.tag===13){var n=bn(e),t=an(e,n);if(t!==null){var r=pe();Be(t,e,n,r)}Ha(e,n)}};Zl=function(){return L};Xl=function(e,n){var t=L;try{return L=e,n()}finally{L=t}};vi=function(e,n,t){switch(n){case"input":if(di(e,t),n=t.name,t.type==="radio"&&n!=null){for(t=e;t.parentNode;)t=t.parentNode;for(t=t.querySelectorAll("input[name="+JSON.stringify(""+n)+'][type="radio"]'),n=0;n<t.length;n++){var r=t[n];if(r!==e&&r.form===e.form){var o=vo(r);if(!o)throw Error(E(90));Tl(r),di(r,o)}}}break;case"textarea":Pl(e,t);break;case"select":n=t.value,n!=null&&at(e,!!t.multiple,n,!1)}};Dl=Da;zl=Hn;var af={usingClientEntryPoint:!1,Events:[ur,Jn,vo,Ll,jl,Da]},Tt={findFiberByHostInstance:On,bundleType:0,version:"18.3.1",rendererPackageName:"react-dom"},sf={bundleType:Tt.bundleType,version:Tt.version,rendererPackageName:Tt.rendererPackageName,rendererConfig:Tt.rendererConfig,overrideHookState:null,overrideHookStateDeletePath:null,overrideHookStateRenamePath:null,overrideProps:null,overridePropsDeletePath:null,overridePropsRenamePath:null,setErrorHandler:null,setSuspenseHandler:null,scheduleUpdate:null,currentDispatcherRef:ln.ReactCurrentDispatcher,findHostInstanceByFiber:function(e){return e=$l(e),e===null?null:e.stateNode},findFiberByHostInstance:Tt.findFiberByHostInstance||rf,findHostInstancesForRefresh:null,scheduleRefresh:null,scheduleRoot:null,setRefreshHandler:null,getCurrentFiber:null,reconcilerVersion:"18.3.1-next-f1338f8080-20240426"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var Nr=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!Nr.isDisabled&&Nr.supportsFiber)try{yo=Nr.inject(sf),We=Nr}catch{}}Se.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=af;Se.createPortal=function(e,n){var t=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!Va(n))throw Error(E(200));return tf(e,n,null,t)};Se.createRoot=function(e,n){if(!Va(e))throw Error(E(299));var t=!1,r="",o=xc;return n!=null&&(n.unstable_strictMode===!0&&(t=!0),n.identifierPrefix!==void 0&&(r=n.identifierPrefix),n.onRecoverableError!==void 0&&(o=n.onRecoverableError)),n=$a(e,1,!1,null,null,t,!1,r,o),e[on]=n.current,Zt(e.nodeType===8?e.parentNode:e),new qa(n)};Se.findDOMNode=function(e){if(e==null)return null;if(e.nodeType===1)return e;var n=e._reactInternals;if(n===void 0)throw typeof e.render=="function"?Error(E(188)):(e=Object.keys(e).join(","),Error(E(268,e)));return e=$l(n),e=e===null?null:e.stateNode,e};Se.flushSync=function(e){return Hn(e)};Se.hydrate=function(e,n,t){if(!Ro(n))throw Error(E(200));return To(null,e,n,!0,t)};Se.hydrateRoot=function(e,n,t){if(!Va(e))throw Error(E(405));var r=t!=null&&t.hydratedSources||null,o=!1,i="",a=xc;if(t!=null&&(t.unstable_strictMode===!0&&(o=!0),t.identifierPrefix!==void 0&&(i=t.identifierPrefix),t.onRecoverableError!==void 0&&(a=t.onRecoverableError)),n=vc(n,null,e,1,t??null,o,!1,i,a),e[on]=n.current,Zt(e),r)for(e=0;e<r.length;e++)t=r[e],o=t._getVersion,o=o(t._source),n.mutableSourceEagerHydrationData==null?n.mutableSourceEagerHydrationData=[t,o]:n.mutableSourceEagerHydrationData.push(t,o);return new No(n)};Se.render=function(e,n,t){if(!Ro(n))throw Error(E(200));return To(null,e,n,!1,t)};Se.unmountComponentAtNode=function(e){if(!Ro(e))throw Error(E(40));return e._reactRootContainer?(Hn(function(){To(null,null,e,!1,function(){e._reactRootContainer=null,e[on]=null})}),!0):!1};Se.unstable_batchedUpdates=Da;Se.unstable_renderSubtreeIntoContainer=function(e,n,t,r){if(!Ro(t))throw Error(E(200));if(e==null||e._reactInternals===void 0)throw Error(E(38));return To(e,n,t,!1,r)};Se.version="18.3.1-next-f1338f8080-20240426";function wc(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(wc)}catch(e){console.error(e)}}wc(),wl.exports=Se;var lf=wl.exports,tl=lf;ii.createRoot=tl.createRoot,ii.hydrateRoot=tl.hydrateRoot;function kc(e){var n,t,r="";if(typeof e=="string"||typeof e=="number")r+=e;else if(typeof e=="object")if(Array.isArray(e)){var o=e.length;for(n=0;n<o;n++)e[n]&&(t=kc(e[n]))&&(r&&(r+=" "),r+=t)}else for(t in e)e[t]&&(r&&(r+=" "),r+=t);return r}function Ec(){for(var e,n,t=0,r="",o=arguments.length;t<o;t++)(e=arguments[t])&&(n=kc(e))&&(r&&(r+=" "),r+=n);return r}var uf=Object.create,Ao=Object.defineProperty,cf=Object.defineProperties,pf=Object.getOwnPropertyDescriptor,df=Object.getOwnPropertyDescriptors,Sc=Object.getOwnPropertyNames,co=Object.getOwnPropertySymbols,ff=Object.getPrototypeOf,Ga=Object.prototype.hasOwnProperty,bc=Object.prototype.propertyIsEnumerable,rl=(e,n,t)=>n in e?Ao(e,n,{enumerable:!0,configurable:!0,writable:!0,value:t}):e[n]=t,Ye=(e,n)=>{for(var t in n||(n={}))Ga.call(n,t)&&rl(e,t,n[t]);if(co)for(var t of co(n))bc.call(n,t)&&rl(e,t,n[t]);return e},Po=(e,n)=>cf(e,df(n)),Cc=(e,n)=>{var t={};for(var r in e)Ga.call(e,r)&&n.indexOf(r)<0&&(t[r]=e[r]);if(e!=null&&co)for(var r of co(e))n.indexOf(r)<0&&bc.call(e,r)&&(t[r]=e[r]);return t},mf=(e,n)=>function(){return n||(0,e[Sc(e)[0]])((n={exports:{}}).exports,n),n.exports},yf=(e,n)=>{for(var t in n)Ao(e,t,{get:n[t],enumerable:!0})},gf=(e,n,t,r)=>{if(n&&typeof n=="object"||typeof n=="function")for(let o of Sc(n))!Ga.call(e,o)&&o!==t&&Ao(e,o,{get:()=>n[o],enumerable:!(r=pf(n,o))||r.enumerable});return e},_f=(e,n,t)=>(t=e!=null?uf(ff(e)):{},gf(!e||!e.__esModule?Ao(t,"default",{value:e,enumerable:!0}):t,e)),hf=mf({"../../node_modules/.pnpm/prismjs@1.29.0_patch_hash=vrxx3pzkik6jpmgpayxfjunetu/node_modules/prismjs/prism.js"(e,n){var t=function(){var r=/(?:^|\s)lang(?:uage)?-([\w-]+)(?=\s|$)/i,o=0,i={},a={util:{encode:function f(m){return m instanceof s?new s(m.type,f(m.content),m.alias):Array.isArray(m)?m.map(f):m.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/\u00a0/g," ")},type:function(f){return Object.prototype.toString.call(f).slice(8,-1)},objId:function(f){return f.__id||Object.defineProperty(f,"__id",{value:++o}),f.__id},clone:function f(m,h){h=h||{};var c,u;switch(a.util.type(m)){case"Object":if(u=a.util.objId(m),h[u])return h[u];c={},h[u]=c;for(var d in m)m.hasOwnProperty(d)&&(c[d]=f(m[d],h));return c;case"Array":return u=a.util.objId(m),h[u]?h[u]:(c=[],h[u]=c,m.forEach(function(v,k){c[k]=f(v,h)}),c);default:return m}},getLanguage:function(f){for(;f;){var m=r.exec(f.className);if(m)return m[1].toLowerCase();f=f.parentElement}return"none"},setLanguage:function(f,m){f.className=f.className.replace(RegExp(r,"gi"),""),f.classList.add("language-"+m)},isActive:function(f,m,h){for(var c="no-"+m;f;){var u=f.classList;if(u.contains(m))return!0;if(u.contains(c))return!1;f=f.parentElement}return!!h}},languages:{plain:i,plaintext:i,text:i,txt:i,extend:function(f,m){var h=a.util.clone(a.languages[f]);for(var c in m)h[c]=m[c];return h},insertBefore:function(f,m,h,c){c=c||a.languages;var u=c[f],d={};for(var v in u)if(u.hasOwnProperty(v)){if(v==m)for(var k in h)h.hasOwnProperty(k)&&(d[k]=h[k]);h.hasOwnProperty(v)||(d[v]=u[v])}var C=c[f];return c[f]=d,a.languages.DFS(a.languages,function(S,N){N===C&&S!=f&&(this[S]=d)}),d},DFS:function f(m,h,c,u){u=u||{};var d=a.util.objId;for(var v in m)if(m.hasOwnProperty(v)){h.call(m,v,m[v],c||v);var k=m[v],C=a.util.type(k);C==="Object"&&!u[d(k)]?(u[d(k)]=!0,f(k,h,null,u)):C==="Array"&&!u[d(k)]&&(u[d(k)]=!0,f(k,h,v,u))}}},plugins:{},highlight:function(f,m,h){var c={code:f,grammar:m,language:h};if(a.hooks.run("before-tokenize",c),!c.grammar)throw new Error('The language "'+c.language+'" has no grammar.');return c.tokens=a.tokenize(c.code,c.grammar),a.hooks.run("after-tokenize",c),s.stringify(a.util.encode(c.tokens),c.language)},tokenize:function(f,m){var h=m.rest;if(h){for(var c in h)m[c]=h[c];delete m.rest}var u=new g;return y(u,u.head,f),p(f,u,m,u.head,0),w(u)},hooks:{all:{},add:function(f,m){var h=a.hooks.all;h[f]=h[f]||[],h[f].push(m)},run:function(f,m){var h=a.hooks.all[f];if(!(!h||!h.length))for(var c=0,u;u=h[c++];)u(m)}},Token:s};function s(f,m,h,c){this.type=f,this.content=m,this.alias=h,this.length=(c||"").length|0}s.stringify=function f(m,h){if(typeof m=="string")return m;if(Array.isArray(m)){var c="";return m.forEach(function(C){c+=f(C,h)}),c}var u={type:m.type,content:f(m.content,h),tag:"span",classes:["token",m.type],attributes:{},language:h},d=m.alias;d&&(Array.isArray(d)?Array.prototype.push.apply(u.classes,d):u.classes.push(d)),a.hooks.run("wrap",u);var v="";for(var k in u.attributes)v+=" "+k+'="'+(u.attributes[k]||"").replace(/"/g,"&quot;")+'"';return"<"+u.tag+' class="'+u.classes.join(" ")+'"'+v+">"+u.content+"</"+u.tag+">"};function l(f,m,h,c){f.lastIndex=m;var u=f.exec(h);if(u&&c&&u[1]){var d=u[1].length;u.index+=d,u[0]=u[0].slice(d)}return u}function p(f,m,h,c,u,d){for(var v in h)if(!(!h.hasOwnProperty(v)||!h[v])){var k=h[v];k=Array.isArray(k)?k:[k];for(var C=0;C<k.length;++C){if(d&&d.cause==v+","+C)return;var S=k[C],N=S.inside,O=!!S.lookbehind,A=!!S.greedy,K=S.alias;if(A&&!S.pattern.global){var ie=S.pattern.toString().match(/[imsuy]*$/)[0];S.pattern=RegExp(S.pattern.source,ie+"g")}for(var un=S.pattern||S,Z=c.next,Ce=u;Z!==m.tail&&!(d&&Ce>=d.reach);Ce+=Z.value.length,Z=Z.next){var He=Z.value;if(m.length>f.length)return;if(!(He instanceof s)){var cn=1,b;if(A){if(b=l(un,Ce,f,O),!b||b.index>=f.length)break;var H=b.index,P=b.index+b[0].length,T=Ce;for(T+=Z.value.length;H>=T;)Z=Z.next,T+=Z.value.length;if(T-=Z.value.length,Ce=T,Z.value instanceof s)continue;for(var j=Z;j!==m.tail&&(T<P||typeof j.value=="string");j=j.next)cn++,T+=j.value.length;cn--,He=f.slice(Ce,T),b.index-=Ce}else if(b=l(un,0,He,O),!b)continue;var H=b.index,Qe=b[0],Fe=He.slice(0,H),Gn=He.slice(H+Qe.length),Oe=Ce+He.length;d&&Oe>d.reach&&(d.reach=Oe);var Ze=Z.prev;Fe&&(Ze=y(m,Ze,Fe),Ce+=Fe.length),_(m,Ze,cn);var Oc=new s(v,N?a.tokenize(Qe,N):Qe,K,Qe);if(Z=y(m,Ze,Oc),Gn&&y(m,Z,Gn),cn>1){var Io={cause:v+","+C,reach:Oe};p(f,m,h,Z.prev,Ce,Io),d&&Io.reach>d.reach&&(d.reach=Io.reach)}}}}}}function g(){var f={value:null,prev:null,next:null},m={value:null,prev:f,next:null};f.next=m,this.head=f,this.tail=m,this.length=0}function y(f,m,h){var c=m.next,u={value:h,prev:m,next:c};return m.next=u,c.prev=u,f.length++,u}function _(f,m,h){for(var c=m.next,u=0;u<h&&c!==f.tail;u++)c=c.next;m.next=c,c.prev=m,f.length-=u}function w(f){for(var m=[],h=f.head.next;h!==f.tail;)m.push(h.value),h=h.next;return m}return a}();n.exports=t,t.default=t}}),x=_f(hf());x.languages.markup={comment:{pattern:/<!--(?:(?!<!--)[\s\S])*?-->/,greedy:!0},prolog:{pattern:/<\?[\s\S]+?\?>/,greedy:!0},doctype:{pattern:/<!DOCTYPE(?:[^>"'[\]]|"[^"]*"|'[^']*')+(?:\[(?:[^<"'\]]|"[^"]*"|'[^']*'|<(?!!--)|<!--(?:[^-]|-(?!->))*-->)*\]\s*)?>/i,greedy:!0,inside:{"internal-subset":{pattern:/(^[^\[]*\[)[\s\S]+(?=\]>$)/,lookbehind:!0,greedy:!0,inside:null},string:{pattern:/"[^"]*"|'[^']*'/,greedy:!0},punctuation:/^<!|>$|[[\]]/,"doctype-tag":/^DOCTYPE/i,name:/[^\s<>'"]+/}},cdata:{pattern:/<!\[CDATA\[[\s\S]*?\]\]>/i,greedy:!0},tag:{pattern:/<\/?(?!\d)[^\s>\/=$<%]+(?:\s(?:\s*[^\s>\/=]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+(?=[\s>]))|(?=[\s/>])))+)?\s*\/?>/,greedy:!0,inside:{tag:{pattern:/^<\/?[^\s>\/]+/,inside:{punctuation:/^<\/?/,namespace:/^[^\s>\/:]+:/}},"special-attr":[],"attr-value":{pattern:/=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+)/,inside:{punctuation:[{pattern:/^=/,alias:"attr-equals"},{pattern:/^(\s*)["']|["']$/,lookbehind:!0}]}},punctuation:/\/?>/,"attr-name":{pattern:/[^\s>\/]+/,inside:{namespace:/^[^\s>\/:]+:/}}}},entity:[{pattern:/&[\da-z]{1,8};/i,alias:"named-entity"},/&#x?[\da-f]{1,8};/i]},x.languages.markup.tag.inside["attr-value"].inside.entity=x.languages.markup.entity,x.languages.markup.doctype.inside["internal-subset"].inside=x.languages.markup,x.hooks.add("wrap",function(e){e.type==="entity"&&(e.attributes.title=e.content.replace(/&amp;/,"&"))}),Object.defineProperty(x.languages.markup.tag,"addInlined",{value:function(e,r){var t={},t=(t["language-"+r]={pattern:/(^<!\[CDATA\[)[\s\S]+?(?=\]\]>$)/i,lookbehind:!0,inside:x.languages[r]},t.cdata=/^<!\[CDATA\[|\]\]>$/i,{"included-cdata":{pattern:/<!\[CDATA\[[\s\S]*?\]\]>/i,inside:t}}),r=(t["language-"+r]={pattern:/[\s\S]+/,inside:x.languages[r]},{});r[e]={pattern:RegExp(/(<__[^>]*>)(?:<!\[CDATA\[(?:[^\]]|\](?!\]>))*\]\]>|(?!<!\[CDATA\[)[\s\S])*?(?=<\/__>)/.source.replace(/__/g,function(){return e}),"i"),lookbehind:!0,greedy:!0,inside:t},x.languages.insertBefore("markup","cdata",r)}}),Object.defineProperty(x.languages.markup.tag,"addAttribute",{value:function(e,n){x.languages.markup.tag.inside["special-attr"].push({pattern:RegExp(/(^|["'\s])/.source+"(?:"+e+")"+/\s*=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+(?=[\s>]))/.source,"i"),lookbehind:!0,inside:{"attr-name":/^[^\s=]+/,"attr-value":{pattern:/=[\s\S]+/,inside:{value:{pattern:/(^=\s*(["']|(?!["'])))\S[\s\S]*(?=\2$)/,lookbehind:!0,alias:[n,"language-"+n],inside:x.languages[n]},punctuation:[{pattern:/^=/,alias:"attr-equals"},/"|'/]}}}})}}),x.languages.html=x.languages.markup,x.languages.mathml=x.languages.markup,x.languages.svg=x.languages.markup,x.languages.xml=x.languages.extend("markup",{}),x.languages.ssml=x.languages.xml,x.languages.atom=x.languages.xml,x.languages.rss=x.languages.xml,function(e){var n={pattern:/\\[\\(){}[\]^$+*?|.]/,alias:"escape"},t=/\\(?:x[\da-fA-F]{2}|u[\da-fA-F]{4}|u\{[\da-fA-F]+\}|0[0-7]{0,2}|[123][0-7]{2}|c[a-zA-Z]|.)/,r="(?:[^\\\\-]|"+t.source+")",r=RegExp(r+"-"+r),o={pattern:/(<|')[^<>']+(?=[>']$)/,lookbehind:!0,alias:"variable"};e.languages.regex={"char-class":{pattern:/((?:^|[^\\])(?:\\\\)*)\[(?:[^\\\]]|\\[\s\S])*\]/,lookbehind:!0,inside:{"char-class-negation":{pattern:/(^\[)\^/,lookbehind:!0,alias:"operator"},"char-class-punctuation":{pattern:/^\[|\]$/,alias:"punctuation"},range:{pattern:r,inside:{escape:t,"range-punctuation":{pattern:/-/,alias:"operator"}}},"special-escape":n,"char-set":{pattern:/\\[wsd]|\\p\{[^{}]+\}/i,alias:"class-name"},escape:t}},"special-escape":n,"char-set":{pattern:/\.|\\[wsd]|\\p\{[^{}]+\}/i,alias:"class-name"},backreference:[{pattern:/\\(?![123][0-7]{2})[1-9]/,alias:"keyword"},{pattern:/\\k<[^<>']+>/,alias:"keyword",inside:{"group-name":o}}],anchor:{pattern:/[$^]|\\[ABbGZz]/,alias:"function"},escape:t,group:[{pattern:/\((?:\?(?:<[^<>']+>|'[^<>']+'|[>:]|<?[=!]|[idmnsuxU]+(?:-[idmnsuxU]+)?:?))?/,alias:"punctuation",inside:{"group-name":o}},{pattern:/\)/,alias:"punctuation"}],quantifier:{pattern:/(?:[+*?]|\{\d+(?:,\d*)?\})[?+]?/,alias:"number"},alternation:{pattern:/\|/,alias:"keyword"}}}(x),x.languages.clike={comment:[{pattern:/(^|[^\\])\/\*[\s\S]*?(?:\*\/|$)/,lookbehind:!0,greedy:!0},{pattern:/(^|[^\\:])\/\/.*/,lookbehind:!0,greedy:!0}],string:{pattern:/(["'])(?:\\(?:\r\n|[\s\S])|(?!\1)[^\\\r\n])*\1/,greedy:!0},"class-name":{pattern:/(\b(?:class|extends|implements|instanceof|interface|new|trait)\s+|\bcatch\s+\()[\w.\\]+/i,lookbehind:!0,inside:{punctuation:/[.\\]/}},keyword:/\b(?:break|catch|continue|do|else|finally|for|function|if|in|instanceof|new|null|return|throw|try|while)\b/,boolean:/\b(?:false|true)\b/,function:/\b\w+(?=\()/,number:/\b0x[\da-f]+\b|(?:\b\d+(?:\.\d*)?|\B\.\d+)(?:e[+-]?\d+)?/i,operator:/[<>]=?|[!=]=?=?|--?|\+\+?|&&?|\|\|?|[?*/~^%]/,punctuation:/[{}[\];(),.:]/},x.languages.javascript=x.languages.extend("clike",{"class-name":[x.languages.clike["class-name"],{pattern:/(^|[^$\w\xA0-\uFFFF])(?!\s)[_$A-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\.(?:constructor|prototype))/,lookbehind:!0}],keyword:[{pattern:/((?:^|\})\s*)catch\b/,lookbehind:!0},{pattern:/(^|[^.]|\.\.\.\s*)\b(?:as|assert(?=\s*\{)|async(?=\s*(?:function\b|\(|[$\w\xA0-\uFFFF]|$))|await|break|case|class|const|continue|debugger|default|delete|do|else|enum|export|extends|finally(?=\s*(?:\{|$))|for|from(?=\s*(?:['"]|$))|function|(?:get|set)(?=\s*(?:[#\[$\w\xA0-\uFFFF]|$))|if|implements|import|in|instanceof|interface|let|new|null|of|package|private|protected|public|return|static|super|switch|this|throw|try|typeof|undefined|var|void|while|with|yield)\b/,lookbehind:!0}],function:/#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*(?:\.\s*(?:apply|bind|call)\s*)?\()/,number:{pattern:RegExp(/(^|[^\w$])/.source+"(?:"+/NaN|Infinity/.source+"|"+/0[bB][01]+(?:_[01]+)*n?/.source+"|"+/0[oO][0-7]+(?:_[0-7]+)*n?/.source+"|"+/0[xX][\dA-Fa-f]+(?:_[\dA-Fa-f]+)*n?/.source+"|"+/\d+(?:_\d+)*n/.source+"|"+/(?:\d+(?:_\d+)*(?:\.(?:\d+(?:_\d+)*)?)?|\.\d+(?:_\d+)*)(?:[Ee][+-]?\d+(?:_\d+)*)?/.source+")"+/(?![\w$])/.source),lookbehind:!0},operator:/--|\+\+|\*\*=?|=>|&&=?|\|\|=?|[!=]==|<<=?|>>>?=?|[-+*/%&|^!=<>]=?|\.{3}|\?\?=?|\?\.?|[~:]/}),x.languages.javascript["class-name"][0].pattern=/(\b(?:class|extends|implements|instanceof|interface|new)\s+)[\w.\\]+/,x.languages.insertBefore("javascript","keyword",{regex:{pattern:RegExp(/((?:^|[^$\w\xA0-\uFFFF."'\])\s]|\b(?:return|yield))\s*)/.source+/\//.source+"(?:"+/(?:\[(?:[^\]\\\r\n]|\\.)*\]|\\.|[^/\\\[\r\n])+\/[dgimyus]{0,7}/.source+"|"+/(?:\[(?:[^[\]\\\r\n]|\\.|\[(?:[^[\]\\\r\n]|\\.|\[(?:[^[\]\\\r\n]|\\.)*\])*\])*\]|\\.|[^/\\\[\r\n])+\/[dgimyus]{0,7}v[dgimyus]{0,7}/.source+")"+/(?=(?:\s|\/\*(?:[^*]|\*(?!\/))*\*\/)*(?:$|[\r\n,.;:})\]]|\/\/))/.source),lookbehind:!0,greedy:!0,inside:{"regex-source":{pattern:/^(\/)[\s\S]+(?=\/[a-z]*$)/,lookbehind:!0,alias:"language-regex",inside:x.languages.regex},"regex-delimiter":/^\/|\/$/,"regex-flags":/^[a-z]+$/}},"function-variable":{pattern:/#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*[=:]\s*(?:async\s*)?(?:\bfunction\b|(?:\((?:[^()]|\([^()]*\))*\)|(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*)\s*=>))/,alias:"function"},parameter:[{pattern:/(function(?:\s+(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*)?\s*\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\))/,lookbehind:!0,inside:x.languages.javascript},{pattern:/(^|[^$\w\xA0-\uFFFF])(?!\s)[_$a-z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*=>)/i,lookbehind:!0,inside:x.languages.javascript},{pattern:/(\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\)\s*=>)/,lookbehind:!0,inside:x.languages.javascript},{pattern:/((?:\b|\s|^)(?!(?:as|async|await|break|case|catch|class|const|continue|debugger|default|delete|do|else|enum|export|extends|finally|for|from|function|get|if|implements|import|in|instanceof|interface|let|new|null|of|package|private|protected|public|return|set|static|super|switch|this|throw|try|typeof|undefined|var|void|while|with|yield)(?![$\w\xA0-\uFFFF]))(?:(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*\s*)\(\s*|\]\s*\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\)\s*\{)/,lookbehind:!0,inside:x.languages.javascript}],constant:/\b[A-Z](?:[A-Z_]|\dx?)*\b/}),x.languages.insertBefore("javascript","string",{hashbang:{pattern:/^#!.*/,greedy:!0,alias:"comment"},"template-string":{pattern:/`(?:\\[\s\S]|\$\{(?:[^{}]|\{(?:[^{}]|\{[^}]*\})*\})+\}|(?!\$\{)[^\\`])*`/,greedy:!0,inside:{"template-punctuation":{pattern:/^`|`$/,alias:"string"},interpolation:{pattern:/((?:^|[^\\])(?:\\{2})*)\$\{(?:[^{}]|\{(?:[^{}]|\{[^}]*\})*\})+\}/,lookbehind:!0,inside:{"interpolation-punctuation":{pattern:/^\$\{|\}$/,alias:"punctuation"},rest:x.languages.javascript}},string:/[\s\S]+/}},"string-property":{pattern:/((?:^|[,{])[ \t]*)(["'])(?:\\(?:\r\n|[\s\S])|(?!\2)[^\\\r\n])*\2(?=\s*:)/m,lookbehind:!0,greedy:!0,alias:"property"}}),x.languages.insertBefore("javascript","operator",{"literal-property":{pattern:/((?:^|[,{])[ \t]*)(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*:)/m,lookbehind:!0,alias:"property"}}),x.languages.markup&&(x.languages.markup.tag.addInlined("script","javascript"),x.languages.markup.tag.addAttribute(/on(?:abort|blur|change|click|composition(?:end|start|update)|dblclick|error|focus(?:in|out)?|key(?:down|up)|load|mouse(?:down|enter|leave|move|out|over|up)|reset|resize|scroll|select|slotchange|submit|unload|wheel)/.source,"javascript")),x.languages.js=x.languages.javascript,x.languages.actionscript=x.languages.extend("javascript",{keyword:/\b(?:as|break|case|catch|class|const|default|delete|do|dynamic|each|else|extends|final|finally|for|function|get|if|implements|import|in|include|instanceof|interface|internal|is|namespace|native|new|null|override|package|private|protected|public|return|set|static|super|switch|this|throw|try|typeof|use|var|void|while|with)\b/,operator:/\+\+|--|(?:[+\-*\/%^]|&&?|\|\|?|<<?|>>?>?|[!=]=?)=?|[~?@]/}),x.languages.actionscript["class-name"].alias="function",delete x.languages.actionscript.parameter,delete x.languages.actionscript["literal-property"],x.languages.markup&&x.languages.insertBefore("actionscript","string",{xml:{pattern:/(^|[^.])<\/?\w+(?:\s+[^\s>\/=]+=("|')(?:\\[\s\S]|(?!\2)[^\\])*\2)*\s*\/?>/,lookbehind:!0,inside:x.languages.markup}}),function(e){var n=/#(?!\{).+/,t={pattern:/#\{[^}]+\}/,alias:"variable"};e.languages.coffeescript=e.languages.extend("javascript",{comment:n,string:[{pattern:/'(?:\\[\s\S]|[^\\'])*'/,greedy:!0},{pattern:/"(?:\\[\s\S]|[^\\"])*"/,greedy:!0,inside:{interpolation:t}}],keyword:/\b(?:and|break|by|catch|class|continue|debugger|delete|do|each|else|extend|extends|false|finally|for|if|in|instanceof|is|isnt|let|loop|namespace|new|no|not|null|of|off|on|or|own|return|super|switch|then|this|throw|true|try|typeof|undefined|unless|until|when|while|window|with|yes|yield)\b/,"class-member":{pattern:/@(?!\d)\w+/,alias:"variable"}}),e.languages.insertBefore("coffeescript","comment",{"multiline-comment":{pattern:/###[\s\S]+?###/,alias:"comment"},"block-regex":{pattern:/\/{3}[\s\S]*?\/{3}/,alias:"regex",inside:{comment:n,interpolation:t}}}),e.languages.insertBefore("coffeescript","string",{"inline-javascript":{pattern:/`(?:\\[\s\S]|[^\\`])*`/,inside:{delimiter:{pattern:/^`|`$/,alias:"punctuation"},script:{pattern:/[\s\S]+/,alias:"language-javascript",inside:e.languages.javascript}}},"multiline-string":[{pattern:/'''[\s\S]*?'''/,greedy:!0,alias:"string"},{pattern:/"""[\s\S]*?"""/,greedy:!0,alias:"string",inside:{interpolation:t}}]}),e.languages.insertBefore("coffeescript","keyword",{property:/(?!\d)\w+(?=\s*:(?!:))/}),delete e.languages.coffeescript["template-string"],e.languages.coffee=e.languages.coffeescript}(x),function(e){var n=e.languages.javadoclike={parameter:{pattern:/(^[\t ]*(?:\/{3}|\*|\/\*\*)\s*@(?:arg|arguments|param)\s+)\w+/m,lookbehind:!0},keyword:{pattern:/(^[\t ]*(?:\/{3}|\*|\/\*\*)\s*|\{)@[a-z][a-zA-Z-]+\b/m,lookbehind:!0},punctuation:/[{}]/};Object.defineProperty(n,"addSupport",{value:function(t,r){(t=typeof t=="string"?[t]:t).forEach(function(o){var i=function(y){y.inside||(y.inside={}),y.inside.rest=r},a="doc-comment";if(s=e.languages[o]){var s,l=s[a];if((l=l||(s=e.languages.insertBefore(o,"comment",{"doc-comment":{pattern:/(^|[^\\])\/\*\*[^/][\s\S]*?(?:\*\/|$)/,lookbehind:!0,alias:"comment"}}))[a])instanceof RegExp&&(l=s[a]={pattern:l}),Array.isArray(l))for(var p=0,g=l.length;p<g;p++)l[p]instanceof RegExp&&(l[p]={pattern:l[p]}),i(l[p]);else i(l)}})}}),n.addSupport(["java","javascript","php"],n)}(x),function(e){var n=/(?:"(?:\\(?:\r\n|[\s\S])|[^"\\\r\n])*"|'(?:\\(?:\r\n|[\s\S])|[^'\\\r\n])*')/,n=(e.languages.css={comment:/\/\*[\s\S]*?\*\//,atrule:{pattern:RegExp("@[\\w-](?:"+/[^;{\s"']|\s+(?!\s)/.source+"|"+n.source+")*?"+/(?:;|(?=\s*\{))/.source),inside:{rule:/^@[\w-]+/,"selector-function-argument":{pattern:/(\bselector\s*\(\s*(?![\s)]))(?:[^()\s]|\s+(?![\s)])|\((?:[^()]|\([^()]*\))*\))+(?=\s*\))/,lookbehind:!0,alias:"selector"},keyword:{pattern:/(^|[^\w-])(?:and|not|only|or)(?![\w-])/,lookbehind:!0}}},url:{pattern:RegExp("\\burl\\((?:"+n.source+"|"+/(?:[^\\\r\n()"']|\\[\s\S])*/.source+")\\)","i"),greedy:!0,inside:{function:/^url/i,punctuation:/^\(|\)$/,string:{pattern:RegExp("^"+n.source+"$"),alias:"url"}}},selector:{pattern:RegExp(`(^|[{}\\s])[^{}\\s](?:[^{};"'\\s]|\\s+(?![\\s{])|`+n.source+")*(?=\\s*\\{)"),lookbehind:!0},string:{pattern:n,greedy:!0},property:{pattern:/(^|[^-\w\xA0-\uFFFF])(?!\s)[-_a-z\xA0-\uFFFF](?:(?!\s)[-\w\xA0-\uFFFF])*(?=\s*:)/i,lookbehind:!0},important:/!important\b/i,function:{pattern:/(^|[^-a-z0-9])[-a-z0-9]+(?=\()/i,lookbehind:!0},punctuation:/[(){};:,]/},e.languages.css.atrule.inside.rest=e.languages.css,e.languages.markup);n&&(n.tag.addInlined("style","css"),n.tag.addAttribute("style","css"))}(x),function(e){var n=/("|')(?:\\(?:\r\n|[\s\S])|(?!\1)[^\\\r\n])*\1/,n=(e.languages.css.selector={pattern:e.languages.css.selector.pattern,lookbehind:!0,inside:n={"pseudo-element":/:(?:after|before|first-letter|first-line|selection)|::[-\w]+/,"pseudo-class":/:[-\w]+/,class:/\.[-\w]+/,id:/#[-\w]+/,attribute:{pattern:RegExp(`\\[(?:[^[\\]"']|`+n.source+")*\\]"),greedy:!0,inside:{punctuation:/^\[|\]$/,"case-sensitivity":{pattern:/(\s)[si]$/i,lookbehind:!0,alias:"keyword"},namespace:{pattern:/^(\s*)(?:(?!\s)[-*\w\xA0-\uFFFF])*\|(?!=)/,lookbehind:!0,inside:{punctuation:/\|$/}},"attr-name":{pattern:/^(\s*)(?:(?!\s)[-\w\xA0-\uFFFF])+/,lookbehind:!0},"attr-value":[n,{pattern:/(=\s*)(?:(?!\s)[-\w\xA0-\uFFFF])+(?=\s*$)/,lookbehind:!0}],operator:/[|~*^$]?=/}},"n-th":[{pattern:/(\(\s*)[+-]?\d*[\dn](?:\s*[+-]\s*\d+)?(?=\s*\))/,lookbehind:!0,inside:{number:/[\dn]+/,operator:/[+-]/}},{pattern:/(\(\s*)(?:even|odd)(?=\s*\))/i,lookbehind:!0}],combinator:/>|\+|~|\|\|/,punctuation:/[(),]/}},e.languages.css.atrule.inside["selector-function-argument"].inside=n,e.languages.insertBefore("css","property",{variable:{pattern:/(^|[^-\w\xA0-\uFFFF])--(?!\s)[-_a-z\xA0-\uFFFF](?:(?!\s)[-\w\xA0-\uFFFF])*/i,lookbehind:!0}}),{pattern:/(\b\d+)(?:%|[a-z]+(?![\w-]))/,lookbehind:!0}),t={pattern:/(^|[^\w.-])-?(?:\d+(?:\.\d+)?|\.\d+)/,lookbehind:!0};e.languages.insertBefore("css","function",{operator:{pattern:/(\s)[+\-*\/](?=\s)/,lookbehind:!0},hexcode:{pattern:/\B#[\da-f]{3,8}\b/i,alias:"color"},color:[{pattern:/(^|[^\w-])(?:AliceBlue|AntiqueWhite|Aqua|Aquamarine|Azure|Beige|Bisque|Black|BlanchedAlmond|Blue|BlueViolet|Brown|BurlyWood|CadetBlue|Chartreuse|Chocolate|Coral|CornflowerBlue|Cornsilk|Crimson|Cyan|DarkBlue|DarkCyan|DarkGoldenRod|DarkGr[ae]y|DarkGreen|DarkKhaki|DarkMagenta|DarkOliveGreen|DarkOrange|DarkOrchid|DarkRed|DarkSalmon|DarkSeaGreen|DarkSlateBlue|DarkSlateGr[ae]y|DarkTurquoise|DarkViolet|DeepPink|DeepSkyBlue|DimGr[ae]y|DodgerBlue|FireBrick|FloralWhite|ForestGreen|Fuchsia|Gainsboro|GhostWhite|Gold|GoldenRod|Gr[ae]y|Green|GreenYellow|HoneyDew|HotPink|IndianRed|Indigo|Ivory|Khaki|Lavender|LavenderBlush|LawnGreen|LemonChiffon|LightBlue|LightCoral|LightCyan|LightGoldenRodYellow|LightGr[ae]y|LightGreen|LightPink|LightSalmon|LightSeaGreen|LightSkyBlue|LightSlateGr[ae]y|LightSteelBlue|LightYellow|Lime|LimeGreen|Linen|Magenta|Maroon|MediumAquaMarine|MediumBlue|MediumOrchid|MediumPurple|MediumSeaGreen|MediumSlateBlue|MediumSpringGreen|MediumTurquoise|MediumVioletRed|MidnightBlue|MintCream|MistyRose|Moccasin|NavajoWhite|Navy|OldLace|Olive|OliveDrab|Orange|OrangeRed|Orchid|PaleGoldenRod|PaleGreen|PaleTurquoise|PaleVioletRed|PapayaWhip|PeachPuff|Peru|Pink|Plum|PowderBlue|Purple|RebeccaPurple|Red|RosyBrown|RoyalBlue|SaddleBrown|Salmon|SandyBrown|SeaGreen|SeaShell|Sienna|Silver|SkyBlue|SlateBlue|SlateGr[ae]y|Snow|SpringGreen|SteelBlue|Tan|Teal|Thistle|Tomato|Transparent|Turquoise|Violet|Wheat|White|WhiteSmoke|Yellow|YellowGreen)(?![\w-])/i,lookbehind:!0},{pattern:/\b(?:hsl|rgb)\(\s*\d{1,3}\s*,\s*\d{1,3}%?\s*,\s*\d{1,3}%?\s*\)\B|\b(?:hsl|rgb)a\(\s*\d{1,3}\s*,\s*\d{1,3}%?\s*,\s*\d{1,3}%?\s*,\s*(?:0|0?\.\d+|1)\s*\)\B/i,inside:{unit:n,number:t,function:/[\w-]+(?=\()/,punctuation:/[(),]/}}],entity:/\\[\da-f]{1,8}/i,unit:n,number:t})}(x),function(e){var n=/[*&][^\s[\]{},]+/,t=/!(?:<[\w\-%#;/?:@&=+$,.!~*'()[\]]+>|(?:[a-zA-Z\d-]*!)?[\w\-%#;/?:@&=+$.~*'()]+)?/,r="(?:"+t.source+"(?:[ 	]+"+n.source+")?|"+n.source+"(?:[ 	]+"+t.source+")?)",o=/(?:[^\s\x00-\x08\x0e-\x1f!"#%&'*,\-:>?@[\]`{|}\x7f-\x84\x86-\x9f\ud800-\udfff\ufffe\uffff]|[?:-]<PLAIN>)(?:[ \t]*(?:(?![#:])<PLAIN>|:<PLAIN>))*/.source.replace(/<PLAIN>/g,function(){return/[^\s\x00-\x08\x0e-\x1f,[\]{}\x7f-\x84\x86-\x9f\ud800-\udfff\ufffe\uffff]/.source}),i=/"(?:[^"\\\r\n]|\\.)*"|'(?:[^'\\\r\n]|\\.)*'/.source;function a(s,l){l=(l||"").replace(/m/g,"")+"m";var p=/([:\-,[{]\s*(?:\s<<prop>>[ \t]+)?)(?:<<value>>)(?=[ \t]*(?:$|,|\]|\}|(?:[\r\n]\s*)?#))/.source.replace(/<<prop>>/g,function(){return r}).replace(/<<value>>/g,function(){return s});return RegExp(p,l)}e.languages.yaml={scalar:{pattern:RegExp(/([\-:]\s*(?:\s<<prop>>[ \t]+)?[|>])[ \t]*(?:((?:\r?\n|\r)[ \t]+)\S[^\r\n]*(?:\2[^\r\n]+)*)/.source.replace(/<<prop>>/g,function(){return r})),lookbehind:!0,alias:"string"},comment:/#.*/,key:{pattern:RegExp(/((?:^|[:\-,[{\r\n?])[ \t]*(?:<<prop>>[ \t]+)?)<<key>>(?=\s*:\s)/.source.replace(/<<prop>>/g,function(){return r}).replace(/<<key>>/g,function(){return"(?:"+o+"|"+i+")"})),lookbehind:!0,greedy:!0,alias:"atrule"},directive:{pattern:/(^[ \t]*)%.+/m,lookbehind:!0,alias:"important"},datetime:{pattern:a(/\d{4}-\d\d?-\d\d?(?:[tT]|[ \t]+)\d\d?:\d{2}:\d{2}(?:\.\d*)?(?:[ \t]*(?:Z|[-+]\d\d?(?::\d{2})?))?|\d{4}-\d{2}-\d{2}|\d\d?:\d{2}(?::\d{2}(?:\.\d*)?)?/.source),lookbehind:!0,alias:"number"},boolean:{pattern:a(/false|true/.source,"i"),lookbehind:!0,alias:"important"},null:{pattern:a(/null|~/.source,"i"),lookbehind:!0,alias:"important"},string:{pattern:a(i),lookbehind:!0,greedy:!0},number:{pattern:a(/[+-]?(?:0x[\da-f]+|0o[0-7]+|(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?|\.inf|\.nan)/.source,"i"),lookbehind:!0},tag:t,important:n,punctuation:/---|[:[\]{}\-,|>?]|\.\.\./},e.languages.yml=e.languages.yaml}(x),function(e){var n=/(?:\\.|[^\\\n\r]|(?:\n|\r\n?)(?![\r\n]))/.source;function t(p){return p=p.replace(/<inner>/g,function(){return n}),RegExp(/((?:^|[^\\])(?:\\{2})*)/.source+"(?:"+p+")")}var r=/(?:\\.|``(?:[^`\r\n]|`(?!`))+``|`[^`\r\n]+`|[^\\|\r\n`])+/.source,o=/\|?__(?:\|__)+\|?(?:(?:\n|\r\n?)|(?![\s\S]))/.source.replace(/__/g,function(){return r}),i=/\|?[ \t]*:?-{3,}:?[ \t]*(?:\|[ \t]*:?-{3,}:?[ \t]*)+\|?(?:\n|\r\n?)/.source,a=(e.languages.markdown=e.languages.extend("markup",{}),e.languages.insertBefore("markdown","prolog",{"front-matter-block":{pattern:/(^(?:\s*[\r\n])?)---(?!.)[\s\S]*?[\r\n]---(?!.)/,lookbehind:!0,greedy:!0,inside:{punctuation:/^---|---$/,"front-matter":{pattern:/\S+(?:\s+\S+)*/,alias:["yaml","language-yaml"],inside:e.languages.yaml}}},blockquote:{pattern:/^>(?:[\t ]*>)*/m,alias:"punctuation"},table:{pattern:RegExp("^"+o+i+"(?:"+o+")*","m"),inside:{"table-data-rows":{pattern:RegExp("^("+o+i+")(?:"+o+")*$"),lookbehind:!0,inside:{"table-data":{pattern:RegExp(r),inside:e.languages.markdown},punctuation:/\|/}},"table-line":{pattern:RegExp("^("+o+")"+i+"$"),lookbehind:!0,inside:{punctuation:/\||:?-{3,}:?/}},"table-header-row":{pattern:RegExp("^"+o+"$"),inside:{"table-header":{pattern:RegExp(r),alias:"important",inside:e.languages.markdown},punctuation:/\|/}}}},code:[{pattern:/((?:^|\n)[ \t]*\n|(?:^|\r\n?)[ \t]*\r\n?)(?: {4}|\t).+(?:(?:\n|\r\n?)(?: {4}|\t).+)*/,lookbehind:!0,alias:"keyword"},{pattern:/^```[\s\S]*?^```$/m,greedy:!0,inside:{"code-block":{pattern:/^(```.*(?:\n|\r\n?))[\s\S]+?(?=(?:\n|\r\n?)^```$)/m,lookbehind:!0},"code-language":{pattern:/^(```).+/,lookbehind:!0},punctuation:/```/}}],title:[{pattern:/\S.*(?:\n|\r\n?)(?:==+|--+)(?=[ \t]*$)/m,alias:"important",inside:{punctuation:/==+$|--+$/}},{pattern:/(^\s*)#.+/m,lookbehind:!0,alias:"important",inside:{punctuation:/^#+|#+$/}}],hr:{pattern:/(^\s*)([*-])(?:[\t ]*\2){2,}(?=\s*$)/m,lookbehind:!0,alias:"punctuation"},list:{pattern:/(^\s*)(?:[*+-]|\d+\.)(?=[\t ].)/m,lookbehind:!0,alias:"punctuation"},"url-reference":{pattern:/!?\[[^\]]+\]:[\t ]+(?:\S+|<(?:\\.|[^>\\])+>)(?:[\t ]+(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\((?:\\.|[^)\\])*\)))?/,inside:{variable:{pattern:/^(!?\[)[^\]]+/,lookbehind:!0},string:/(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\((?:\\.|[^)\\])*\))$/,punctuation:/^[\[\]!:]|[<>]/},alias:"url"},bold:{pattern:t(/\b__(?:(?!_)<inner>|_(?:(?!_)<inner>)+_)+__\b|\*\*(?:(?!\*)<inner>|\*(?:(?!\*)<inner>)+\*)+\*\*/.source),lookbehind:!0,greedy:!0,inside:{content:{pattern:/(^..)[\s\S]+(?=..$)/,lookbehind:!0,inside:{}},punctuation:/\*\*|__/}},italic:{pattern:t(/\b_(?:(?!_)<inner>|__(?:(?!_)<inner>)+__)+_\b|\*(?:(?!\*)<inner>|\*\*(?:(?!\*)<inner>)+\*\*)+\*/.source),lookbehind:!0,greedy:!0,inside:{content:{pattern:/(^.)[\s\S]+(?=.$)/,lookbehind:!0,inside:{}},punctuation:/[*_]/}},strike:{pattern:t(/(~~?)(?:(?!~)<inner>)+\2/.source),lookbehind:!0,greedy:!0,inside:{content:{pattern:/(^~~?)[\s\S]+(?=\1$)/,lookbehind:!0,inside:{}},punctuation:/~~?/}},"code-snippet":{pattern:/(^|[^\\`])(?:``[^`\r\n]+(?:`[^`\r\n]+)*``(?!`)|`[^`\r\n]+`(?!`))/,lookbehind:!0,greedy:!0,alias:["code","keyword"]},url:{pattern:t(/!?\[(?:(?!\])<inner>)+\](?:\([^\s)]+(?:[\t ]+"(?:\\.|[^"\\])*")?\)|[ \t]?\[(?:(?!\])<inner>)+\])/.source),lookbehind:!0,greedy:!0,inside:{operator:/^!/,content:{pattern:/(^\[)[^\]]+(?=\])/,lookbehind:!0,inside:{}},variable:{pattern:/(^\][ \t]?\[)[^\]]+(?=\]$)/,lookbehind:!0},url:{pattern:/(^\]\()[^\s)]+/,lookbehind:!0},string:{pattern:/(^[ \t]+)"(?:\\.|[^"\\])*"(?=\)$)/,lookbehind:!0}}}}),["url","bold","italic","strike"].forEach(function(p){["url","bold","italic","strike","code-snippet"].forEach(function(g){p!==g&&(e.languages.markdown[p].inside.content.inside[g]=e.languages.markdown[g])})}),e.hooks.add("after-tokenize",function(p){p.language!=="markdown"&&p.language!=="md"||function g(y){if(y&&typeof y!="string")for(var _=0,w=y.length;_<w;_++){var f,m=y[_];m.type!=="code"?g(m.content):(f=m.content[1],m=m.content[3],f&&m&&f.type==="code-language"&&m.type==="code-block"&&typeof f.content=="string"&&(f=f.content.replace(/\b#/g,"sharp").replace(/\b\+\+/g,"pp"),f="language-"+(f=(/[a-z][\w-]*/i.exec(f)||[""])[0].toLowerCase()),m.alias?typeof m.alias=="string"?m.alias=[m.alias,f]:m.alias.push(f):m.alias=[f]))}}(p.tokens)}),e.hooks.add("wrap",function(p){if(p.type==="code-block"){for(var g="",y=0,_=p.classes.length;y<_;y++){var w=p.classes[y],w=/language-(.+)/.exec(w);if(w){g=w[1];break}}var f,m=e.languages[g];m?p.content=e.highlight(function(h){return h=h.replace(a,""),h=h.replace(/&(\w{1,8}|#x?[\da-f]{1,8});/gi,function(c,u){var d;return(u=u.toLowerCase())[0]==="#"?(d=u[1]==="x"?parseInt(u.slice(2),16):Number(u.slice(1)),l(d)):s[u]||c})}(p.content),m,g):g&&g!=="none"&&e.plugins.autoloader&&(f="md-"+new Date().valueOf()+"-"+Math.floor(1e16*Math.random()),p.attributes.id=f,e.plugins.autoloader.loadLanguages(g,function(){var h=document.getElementById(f);h&&(h.innerHTML=e.highlight(h.textContent,e.languages[g],g))}))}}),RegExp(e.languages.markup.tag.pattern.source,"gi")),s={amp:"&",lt:"<",gt:">",quot:'"'},l=String.fromCodePoint||String.fromCharCode;e.languages.md=e.languages.markdown}(x),x.languages.graphql={comment:/#.*/,description:{pattern:/(?:"""(?:[^"]|(?!""")")*"""|"(?:\\.|[^\\"\r\n])*")(?=\s*[a-z_])/i,greedy:!0,alias:"string",inside:{"language-markdown":{pattern:/(^"(?:"")?)(?!\1)[\s\S]+(?=\1$)/,lookbehind:!0,inside:x.languages.markdown}}},string:{pattern:/"""(?:[^"]|(?!""")")*"""|"(?:\\.|[^\\"\r\n])*"/,greedy:!0},number:/(?:\B-|\b)\d+(?:\.\d+)?(?:e[+-]?\d+)?\b/i,boolean:/\b(?:false|true)\b/,variable:/\$[a-z_]\w*/i,directive:{pattern:/@[a-z_]\w*/i,alias:"function"},"attr-name":{pattern:/\b[a-z_]\w*(?=\s*(?:\((?:[^()"]|"(?:\\.|[^\\"\r\n])*")*\))?:)/i,greedy:!0},"atom-input":{pattern:/\b[A-Z]\w*Input\b/,alias:"class-name"},scalar:/\b(?:Boolean|Float|ID|Int|String)\b/,constant:/\b[A-Z][A-Z_\d]*\b/,"class-name":{pattern:/(\b(?:enum|implements|interface|on|scalar|type|union)\s+|&\s*|:\s*|\[)[A-Z_]\w*/,lookbehind:!0},fragment:{pattern:/(\bfragment\s+|\.{3}\s*(?!on\b))[a-zA-Z_]\w*/,lookbehind:!0,alias:"function"},"definition-mutation":{pattern:/(\bmutation\s+)[a-zA-Z_]\w*/,lookbehind:!0,alias:"function"},"definition-query":{pattern:/(\bquery\s+)[a-zA-Z_]\w*/,lookbehind:!0,alias:"function"},keyword:/\b(?:directive|enum|extend|fragment|implements|input|interface|mutation|on|query|repeatable|scalar|schema|subscription|type|union)\b/,operator:/[!=|&]|\.{3}/,"property-query":/\w+(?=\s*\()/,object:/\w+(?=\s*\{)/,punctuation:/[!(){}\[\]:=,]/,property:/\w+/},x.hooks.add("after-tokenize",function(e){if(e.language==="graphql")for(var n=e.tokens.filter(function(f){return typeof f!="string"&&f.type!=="comment"&&f.type!=="scalar"}),t=0;t<n.length;){var r=n[t++];if(r.type==="keyword"&&r.content==="mutation"){var o=[];if(y(["definition-mutation","punctuation"])&&g(1).content==="("){t+=2;var i=_(/^\($/,/^\)$/);if(i===-1)continue;for(;t<i;t++){var a=g(0);a.type==="variable"&&(w(a,"variable-input"),o.push(a.content))}t=i+1}if(y(["punctuation","property-query"])&&g(0).content==="{"&&(t++,w(g(0),"property-mutation"),0<o.length)){var s=_(/^\{$/,/^\}$/);if(s!==-1)for(var l=t;l<s;l++){var p=n[l];p.type==="variable"&&0<=o.indexOf(p.content)&&w(p,"variable-input")}}}}function g(f){return n[t+f]}function y(f,m){m=m||0;for(var h=0;h<f.length;h++){var c=g(h+m);if(!c||c.type!==f[h])return}return 1}function _(f,m){for(var h=1,c=t;c<n.length;c++){var u=n[c],d=u.content;if(u.type==="punctuation"&&typeof d=="string"){if(f.test(d))h++;else if(m.test(d)&&--h===0)return c}}return-1}function w(f,m){var h=f.alias;h?Array.isArray(h)||(f.alias=h=[h]):f.alias=h=[],h.push(m)}}),x.languages.sql={comment:{pattern:/(^|[^\\])(?:\/\*[\s\S]*?\*\/|(?:--|\/\/|#).*)/,lookbehind:!0},variable:[{pattern:/@(["'`])(?:\\[\s\S]|(?!\1)[^\\])+\1/,greedy:!0},/@[\w.$]+/],string:{pattern:/(^|[^@\\])("|')(?:\\[\s\S]|(?!\2)[^\\]|\2\2)*\2/,greedy:!0,lookbehind:!0},identifier:{pattern:/(^|[^@\\])`(?:\\[\s\S]|[^`\\]|``)*`/,greedy:!0,lookbehind:!0,inside:{punctuation:/^`|`$/}},function:/\b(?:AVG|COUNT|FIRST|FORMAT|LAST|LCASE|LEN|MAX|MID|MIN|MOD|NOW|ROUND|SUM|UCASE)(?=\s*\()/i,keyword:/\b(?:ACTION|ADD|AFTER|ALGORITHM|ALL|ALTER|ANALYZE|ANY|APPLY|AS|ASC|AUTHORIZATION|AUTO_INCREMENT|BACKUP|BDB|BEGIN|BERKELEYDB|BIGINT|BINARY|BIT|BLOB|BOOL|BOOLEAN|BREAK|BROWSE|BTREE|BULK|BY|CALL|CASCADED?|CASE|CHAIN|CHAR(?:ACTER|SET)?|CHECK(?:POINT)?|CLOSE|CLUSTERED|COALESCE|COLLATE|COLUMNS?|COMMENT|COMMIT(?:TED)?|COMPUTE|CONNECT|CONSISTENT|CONSTRAINT|CONTAINS(?:TABLE)?|CONTINUE|CONVERT|CREATE|CROSS|CURRENT(?:_DATE|_TIME|_TIMESTAMP|_USER)?|CURSOR|CYCLE|DATA(?:BASES?)?|DATE(?:TIME)?|DAY|DBCC|DEALLOCATE|DEC|DECIMAL|DECLARE|DEFAULT|DEFINER|DELAYED|DELETE|DELIMITERS?|DENY|DESC|DESCRIBE|DETERMINISTIC|DISABLE|DISCARD|DISK|DISTINCT|DISTINCTROW|DISTRIBUTED|DO|DOUBLE|DROP|DUMMY|DUMP(?:FILE)?|DUPLICATE|ELSE(?:IF)?|ENABLE|ENCLOSED|END|ENGINE|ENUM|ERRLVL|ERRORS|ESCAPED?|EXCEPT|EXEC(?:UTE)?|EXISTS|EXIT|EXPLAIN|EXTENDED|FETCH|FIELDS|FILE|FILLFACTOR|FIRST|FIXED|FLOAT|FOLLOWING|FOR(?: EACH ROW)?|FORCE|FOREIGN|FREETEXT(?:TABLE)?|FROM|FULL|FUNCTION|GEOMETRY(?:COLLECTION)?|GLOBAL|GOTO|GRANT|GROUP|HANDLER|HASH|HAVING|HOLDLOCK|HOUR|IDENTITY(?:COL|_INSERT)?|IF|IGNORE|IMPORT|INDEX|INFILE|INNER|INNODB|INOUT|INSERT|INT|INTEGER|INTERSECT|INTERVAL|INTO|INVOKER|ISOLATION|ITERATE|JOIN|KEYS?|KILL|LANGUAGE|LAST|LEAVE|LEFT|LEVEL|LIMIT|LINENO|LINES|LINESTRING|LOAD|LOCAL|LOCK|LONG(?:BLOB|TEXT)|LOOP|MATCH(?:ED)?|MEDIUM(?:BLOB|INT|TEXT)|MERGE|MIDDLEINT|MINUTE|MODE|MODIFIES|MODIFY|MONTH|MULTI(?:LINESTRING|POINT|POLYGON)|NATIONAL|NATURAL|NCHAR|NEXT|NO|NONCLUSTERED|NULLIF|NUMERIC|OFF?|OFFSETS?|ON|OPEN(?:DATASOURCE|QUERY|ROWSET)?|OPTIMIZE|OPTION(?:ALLY)?|ORDER|OUT(?:ER|FILE)?|OVER|PARTIAL|PARTITION|PERCENT|PIVOT|PLAN|POINT|POLYGON|PRECEDING|PRECISION|PREPARE|PREV|PRIMARY|PRINT|PRIVILEGES|PROC(?:EDURE)?|PUBLIC|PURGE|QUICK|RAISERROR|READS?|REAL|RECONFIGURE|REFERENCES|RELEASE|RENAME|REPEAT(?:ABLE)?|REPLACE|REPLICATION|REQUIRE|RESIGNAL|RESTORE|RESTRICT|RETURN(?:ING|S)?|REVOKE|RIGHT|ROLLBACK|ROUTINE|ROW(?:COUNT|GUIDCOL|S)?|RTREE|RULE|SAVE(?:POINT)?|SCHEMA|SECOND|SELECT|SERIAL(?:IZABLE)?|SESSION(?:_USER)?|SET(?:USER)?|SHARE|SHOW|SHUTDOWN|SIMPLE|SMALLINT|SNAPSHOT|SOME|SONAME|SQL|START(?:ING)?|STATISTICS|STATUS|STRIPED|SYSTEM_USER|TABLES?|TABLESPACE|TEMP(?:ORARY|TABLE)?|TERMINATED|TEXT(?:SIZE)?|THEN|TIME(?:STAMP)?|TINY(?:BLOB|INT|TEXT)|TOP?|TRAN(?:SACTIONS?)?|TRIGGER|TRUNCATE|TSEQUAL|TYPES?|UNBOUNDED|UNCOMMITTED|UNDEFINED|UNION|UNIQUE|UNLOCK|UNPIVOT|UNSIGNED|UPDATE(?:TEXT)?|USAGE|USE|USER|USING|VALUES?|VAR(?:BINARY|CHAR|CHARACTER|YING)|VIEW|WAITFOR|WARNINGS|WHEN|WHERE|WHILE|WITH(?: ROLLUP|IN)?|WORK|WRITE(?:TEXT)?|YEAR)\b/i,boolean:/\b(?:FALSE|NULL|TRUE)\b/i,number:/\b0x[\da-f]+\b|\b\d+(?:\.\d*)?|\B\.\d+\b/i,operator:/[-+*\/=%^~]|&&?|\|\|?|!=?|<(?:=>?|<|>)?|>[>=]?|\b(?:AND|BETWEEN|DIV|ILIKE|IN|IS|LIKE|NOT|OR|REGEXP|RLIKE|SOUNDS LIKE|XOR)\b/i,punctuation:/[;[\]()`,.]/},function(e){var n=e.languages.javascript["template-string"],t=n.pattern.source,r=n.inside.interpolation,o=r.inside["interpolation-punctuation"],i=r.pattern.source;function a(y,_){if(e.languages[y])return{pattern:RegExp("((?:"+_+")\\s*)"+t),lookbehind:!0,greedy:!0,inside:{"template-punctuation":{pattern:/^`|`$/,alias:"string"},"embedded-code":{pattern:/[\s\S]+/,alias:y}}}}function s(y,_,w){return y={code:y,grammar:_,language:w},e.hooks.run("before-tokenize",y),y.tokens=e.tokenize(y.code,y.grammar),e.hooks.run("after-tokenize",y),y.tokens}function l(y,_,w){var h=e.tokenize(y,{interpolation:{pattern:RegExp(i),lookbehind:!0}}),f=0,m={},h=s(h.map(function(u){if(typeof u=="string")return u;for(var d,v,u=u.content;y.indexOf((v=f++,d="___"+w.toUpperCase()+"_"+v+"___"))!==-1;);return m[d]=u,d}).join(""),_,w),c=Object.keys(m);return f=0,function u(d){for(var v=0;v<d.length;v++){if(f>=c.length)return;var k,C,S,N,O,A,K,ie=d[v];typeof ie=="string"||typeof ie.content=="string"?(k=c[f],(K=(A=typeof ie=="string"?ie:ie.content).indexOf(k))!==-1&&(++f,C=A.substring(0,K),O=m[k],S=void 0,(N={})["interpolation-punctuation"]=o,(N=e.tokenize(O,N)).length===3&&((S=[1,1]).push.apply(S,s(N[1],e.languages.javascript,"javascript")),N.splice.apply(N,S)),S=new e.Token("interpolation",N,r.alias,O),N=A.substring(K+k.length),O=[],C&&O.push(C),O.push(S),N&&(u(A=[N]),O.push.apply(O,A)),typeof ie=="string"?(d.splice.apply(d,[v,1].concat(O)),v+=O.length-1):ie.content=O)):(K=ie.content,Array.isArray(K)?u(K):u([K]))}}(h),new e.Token(w,h,"language-"+w,y)}e.languages.javascript["template-string"]=[a("css",/\b(?:styled(?:\([^)]*\))?(?:\s*\.\s*\w+(?:\([^)]*\))*)*|css(?:\s*\.\s*(?:global|resolve))?|createGlobalStyle|keyframes)/.source),a("html",/\bhtml|\.\s*(?:inner|outer)HTML\s*\+?=/.source),a("svg",/\bsvg/.source),a("markdown",/\b(?:markdown|md)/.source),a("graphql",/\b(?:gql|graphql(?:\s*\.\s*experimental)?)/.source),a("sql",/\bsql/.source),n].filter(Boolean);var p={javascript:!0,js:!0,typescript:!0,ts:!0,jsx:!0,tsx:!0};function g(y){return typeof y=="string"?y:Array.isArray(y)?y.map(g).join(""):g(y.content)}e.hooks.add("after-tokenize",function(y){y.language in p&&function _(w){for(var f=0,m=w.length;f<m;f++){var h,c,u,d=w[f];typeof d!="string"&&(h=d.content,Array.isArray(h)?d.type==="template-string"?(d=h[1],h.length===3&&typeof d!="string"&&d.type==="embedded-code"&&(c=g(d),d=d.alias,d=Array.isArray(d)?d[0]:d,u=e.languages[d])&&(h[1]=l(c,u,d))):_(h):typeof h!="string"&&_([h]))}}(y.tokens)})}(x),function(e){e.languages.typescript=e.languages.extend("javascript",{"class-name":{pattern:/(\b(?:class|extends|implements|instanceof|interface|new|type)\s+)(?!keyof\b)(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?:\s*<(?:[^<>]|<(?:[^<>]|<[^<>]*>)*>)*>)?/,lookbehind:!0,greedy:!0,inside:null},builtin:/\b(?:Array|Function|Promise|any|boolean|console|never|number|string|symbol|unknown)\b/}),e.languages.typescript.keyword.push(/\b(?:abstract|declare|is|keyof|readonly|require)\b/,/\b(?:asserts|infer|interface|module|namespace|type)\b(?=\s*(?:[{_$a-zA-Z\xA0-\uFFFF]|$))/,/\btype\b(?=\s*(?:[\{*]|$))/),delete e.languages.typescript.parameter,delete e.languages.typescript["literal-property"];var n=e.languages.extend("typescript",{});delete n["class-name"],e.languages.typescript["class-name"].inside=n,e.languages.insertBefore("typescript","function",{decorator:{pattern:/@[$\w\xA0-\uFFFF]+/,inside:{at:{pattern:/^@/,alias:"operator"},function:/^[\s\S]+/}},"generic-function":{pattern:/#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*\s*<(?:[^<>]|<(?:[^<>]|<[^<>]*>)*>)*>(?=\s*\()/,greedy:!0,inside:{function:/^#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*/,generic:{pattern:/<[\s\S]+/,alias:"class-name",inside:n}}}}),e.languages.ts=e.languages.typescript}(x),function(e){var n=e.languages.javascript,t=/\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})+\}/.source,r="(@(?:arg|argument|param|property)\\s+(?:"+t+"\\s+)?)";e.languages.jsdoc=e.languages.extend("javadoclike",{parameter:{pattern:RegExp(r+/(?:(?!\s)[$\w\xA0-\uFFFF.])+(?=\s|$)/.source),lookbehind:!0,inside:{punctuation:/\./}}}),e.languages.insertBefore("jsdoc","keyword",{"optional-parameter":{pattern:RegExp(r+/\[(?:(?!\s)[$\w\xA0-\uFFFF.])+(?:=[^[\]]+)?\](?=\s|$)/.source),lookbehind:!0,inside:{parameter:{pattern:/(^\[)[$\w\xA0-\uFFFF\.]+/,lookbehind:!0,inside:{punctuation:/\./}},code:{pattern:/(=)[\s\S]*(?=\]$)/,lookbehind:!0,inside:n,alias:"language-javascript"},punctuation:/[=[\]]/}},"class-name":[{pattern:RegExp(/(@(?:augments|class|extends|interface|memberof!?|template|this|typedef)\s+(?:<TYPE>\s+)?)[A-Z]\w*(?:\.[A-Z]\w*)*/.source.replace(/<TYPE>/g,function(){return t})),lookbehind:!0,inside:{punctuation:/\./}},{pattern:RegExp("(@[a-z]+\\s+)"+t),lookbehind:!0,inside:{string:n.string,number:n.number,boolean:n.boolean,keyword:e.languages.typescript.keyword,operator:/=>|\.\.\.|[&|?:*]/,punctuation:/[.,;=<>{}()[\]]/}}],example:{pattern:/(@example\s+(?!\s))(?:[^@\s]|\s+(?!\s))+?(?=\s*(?:\*\s*)?(?:@\w|\*\/))/,lookbehind:!0,inside:{code:{pattern:/^([\t ]*(?:\*\s*)?)\S.*$/m,lookbehind:!0,inside:n,alias:"language-javascript"}}}}),e.languages.javadoclike.addSupport("javascript",e.languages.jsdoc)}(x),function(e){e.languages.flow=e.languages.extend("javascript",{}),e.languages.insertBefore("flow","keyword",{type:[{pattern:/\b(?:[Bb]oolean|Function|[Nn]umber|[Ss]tring|[Ss]ymbol|any|mixed|null|void)\b/,alias:"class-name"}]}),e.languages.flow["function-variable"].pattern=/(?!\s)[_$a-z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*=\s*(?:function\b|(?:\([^()]*\)(?:\s*:\s*\w+)?|(?!\s)[_$a-z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*)\s*=>))/i,delete e.languages.flow.parameter,e.languages.insertBefore("flow","operator",{"flow-punctuation":{pattern:/\{\||\|\}/,alias:"punctuation"}}),Array.isArray(e.languages.flow.keyword)||(e.languages.flow.keyword=[e.languages.flow.keyword]),e.languages.flow.keyword.unshift({pattern:/(^|[^$]\b)(?:Class|declare|opaque|type)\b(?!\$)/,lookbehind:!0},{pattern:/(^|[^$]\B)\$(?:Diff|Enum|Exact|Keys|ObjMap|PropertyType|Record|Shape|Subtype|Supertype|await)\b(?!\$)/,lookbehind:!0})}(x),x.languages.n4js=x.languages.extend("javascript",{keyword:/\b(?:Array|any|boolean|break|case|catch|class|const|constructor|continue|debugger|declare|default|delete|do|else|enum|export|extends|false|finally|for|from|function|get|if|implements|import|in|instanceof|interface|let|module|new|null|number|package|private|protected|public|return|set|static|string|super|switch|this|throw|true|try|typeof|var|void|while|with|yield)\b/}),x.languages.insertBefore("n4js","constant",{annotation:{pattern:/@+\w+/,alias:"operator"}}),x.languages.n4jsd=x.languages.n4js,function(e){function n(a,s){return RegExp(a.replace(/<ID>/g,function(){return/(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*/.source}),s)}e.languages.insertBefore("javascript","function-variable",{"method-variable":{pattern:RegExp("(\\.\\s*)"+e.languages.javascript["function-variable"].pattern.source),lookbehind:!0,alias:["function-variable","method","function","property-access"]}}),e.languages.insertBefore("javascript","function",{method:{pattern:RegExp("(\\.\\s*)"+e.languages.javascript.function.source),lookbehind:!0,alias:["function","property-access"]}}),e.languages.insertBefore("javascript","constant",{"known-class-name":[{pattern:/\b(?:(?:Float(?:32|64)|(?:Int|Uint)(?:8|16|32)|Uint8Clamped)?Array|ArrayBuffer|BigInt|Boolean|DataView|Date|Error|Function|Intl|JSON|(?:Weak)?(?:Map|Set)|Math|Number|Object|Promise|Proxy|Reflect|RegExp|String|Symbol|WebAssembly)\b/,alias:"class-name"},{pattern:/\b(?:[A-Z]\w*)Error\b/,alias:"class-name"}]}),e.languages.insertBefore("javascript","keyword",{imports:{pattern:n(/(\bimport\b\s*)(?:<ID>(?:\s*,\s*(?:\*\s*as\s+<ID>|\{[^{}]*\}))?|\*\s*as\s+<ID>|\{[^{}]*\})(?=\s*\bfrom\b)/.source),lookbehind:!0,inside:e.languages.javascript},exports:{pattern:n(/(\bexport\b\s*)(?:\*(?:\s*as\s+<ID>)?(?=\s*\bfrom\b)|\{[^{}]*\})/.source),lookbehind:!0,inside:e.languages.javascript}}),e.languages.javascript.keyword.unshift({pattern:/\b(?:as|default|export|from|import)\b/,alias:"module"},{pattern:/\b(?:await|break|catch|continue|do|else|finally|for|if|return|switch|throw|try|while|yield)\b/,alias:"control-flow"},{pattern:/\bnull\b/,alias:["null","nil"]},{pattern:/\bundefined\b/,alias:"nil"}),e.languages.insertBefore("javascript","operator",{spread:{pattern:/\.{3}/,alias:"operator"},arrow:{pattern:/=>/,alias:"operator"}}),e.languages.insertBefore("javascript","punctuation",{"property-access":{pattern:n(/(\.\s*)#?<ID>/.source),lookbehind:!0},"maybe-class-name":{pattern:/(^|[^$\w\xA0-\uFFFF])[A-Z][$\w\xA0-\uFFFF]+/,lookbehind:!0},dom:{pattern:/\b(?:document|(?:local|session)Storage|location|navigator|performance|window)\b/,alias:"variable"},console:{pattern:/\bconsole(?=\s*\.)/,alias:"class-name"}});for(var t=["function","function-variable","method","method-variable","property-access"],r=0;r<t.length;r++){var i=t[r],o=e.languages.javascript[i],i=(o=e.util.type(o)==="RegExp"?e.languages.javascript[i]={pattern:o}:o).inside||{};(o.inside=i)["maybe-class-name"]=/^[A-Z][\s\S]*/}}(x),function(e){var n=e.util.clone(e.languages.javascript),t=/(?:\s|\/\/.*(?!.)|\/\*(?:[^*]|\*(?!\/))\*\/)/.source,r=/(?:\{(?:\{(?:\{[^{}]*\}|[^{}])*\}|[^{}])*\})/.source,o=/(?:\{<S>*\.{3}(?:[^{}]|<BRACES>)*\})/.source;function i(l,p){return l=l.replace(/<S>/g,function(){return t}).replace(/<BRACES>/g,function(){return r}).replace(/<SPREAD>/g,function(){return o}),RegExp(l,p)}o=i(o).source,e.languages.jsx=e.languages.extend("markup",n),e.languages.jsx.tag.pattern=i(/<\/?(?:[\w.:-]+(?:<S>+(?:[\w.:$-]+(?:=(?:"(?:\\[\s\S]|[^\\"])*"|'(?:\\[\s\S]|[^\\'])*'|[^\s{'"/>=]+|<BRACES>))?|<SPREAD>))*<S>*\/?)?>/.source),e.languages.jsx.tag.inside.tag.pattern=/^<\/?[^\s>\/]*/,e.languages.jsx.tag.inside["attr-value"].pattern=/=(?!\{)(?:"(?:\\[\s\S]|[^\\"])*"|'(?:\\[\s\S]|[^\\'])*'|[^\s'">]+)/,e.languages.jsx.tag.inside.tag.inside["class-name"]=/^[A-Z]\w*(?:\.[A-Z]\w*)*$/,e.languages.jsx.tag.inside.comment=n.comment,e.languages.insertBefore("inside","attr-name",{spread:{pattern:i(/<SPREAD>/.source),inside:e.languages.jsx}},e.languages.jsx.tag),e.languages.insertBefore("inside","special-attr",{script:{pattern:i(/=<BRACES>/.source),alias:"language-javascript",inside:{"script-punctuation":{pattern:/^=(?=\{)/,alias:"punctuation"},rest:e.languages.jsx}}},e.languages.jsx.tag);function a(l){for(var p=[],g=0;g<l.length;g++){var y=l[g],_=!1;typeof y!="string"&&(y.type==="tag"&&y.content[0]&&y.content[0].type==="tag"?y.content[0].content[0].content==="</"?0<p.length&&p[p.length-1].tagName===s(y.content[0].content[1])&&p.pop():y.content[y.content.length-1].content!=="/>"&&p.push({tagName:s(y.content[0].content[1]),openedBraces:0}):0<p.length&&y.type==="punctuation"&&y.content==="{"?p[p.length-1].openedBraces++:0<p.length&&0<p[p.length-1].openedBraces&&y.type==="punctuation"&&y.content==="}"?p[p.length-1].openedBraces--:_=!0),(_||typeof y=="string")&&0<p.length&&p[p.length-1].openedBraces===0&&(_=s(y),g<l.length-1&&(typeof l[g+1]=="string"||l[g+1].type==="plain-text")&&(_+=s(l[g+1]),l.splice(g+1,1)),0<g&&(typeof l[g-1]=="string"||l[g-1].type==="plain-text")&&(_=s(l[g-1])+_,l.splice(g-1,1),g--),l[g]=new e.Token("plain-text",_,null,_)),y.content&&typeof y.content!="string"&&a(y.content)}}var s=function(l){return l?typeof l=="string"?l:typeof l.content=="string"?l.content:l.content.map(s).join(""):""};e.hooks.add("after-tokenize",function(l){l.language!=="jsx"&&l.language!=="tsx"||a(l.tokens)})}(x),function(e){var n=e.util.clone(e.languages.typescript),n=(e.languages.tsx=e.languages.extend("jsx",n),delete e.languages.tsx.parameter,delete e.languages.tsx["literal-property"],e.languages.tsx.tag);n.pattern=RegExp(/(^|[^\w$]|(?=<\/))/.source+"(?:"+n.pattern.source+")",n.pattern.flags),n.lookbehind=!0}(x),x.languages.swift={comment:{pattern:/(^|[^\\:])(?:\/\/.*|\/\*(?:[^/*]|\/(?!\*)|\*(?!\/)|\/\*(?:[^*]|\*(?!\/))*\*\/)*\*\/)/,lookbehind:!0,greedy:!0},"string-literal":[{pattern:RegExp(/(^|[^"#])/.source+"(?:"+/"(?:\\(?:\((?:[^()]|\([^()]*\))*\)|\r\n|[^(])|[^\\\r\n"])*"/.source+"|"+/"""(?:\\(?:\((?:[^()]|\([^()]*\))*\)|[^(])|[^\\"]|"(?!""))*"""/.source+")"+/(?!["#])/.source),lookbehind:!0,greedy:!0,inside:{interpolation:{pattern:/(\\\()(?:[^()]|\([^()]*\))*(?=\))/,lookbehind:!0,inside:null},"interpolation-punctuation":{pattern:/^\)|\\\($/,alias:"punctuation"},punctuation:/\\(?=[\r\n])/,string:/[\s\S]+/}},{pattern:RegExp(/(^|[^"#])(#+)/.source+"(?:"+/"(?:\\(?:#+\((?:[^()]|\([^()]*\))*\)|\r\n|[^#])|[^\\\r\n])*?"/.source+"|"+/"""(?:\\(?:#+\((?:[^()]|\([^()]*\))*\)|[^#])|[^\\])*?"""/.source+")\\2"),lookbehind:!0,greedy:!0,inside:{interpolation:{pattern:/(\\#+\()(?:[^()]|\([^()]*\))*(?=\))/,lookbehind:!0,inside:null},"interpolation-punctuation":{pattern:/^\)|\\#+\($/,alias:"punctuation"},string:/[\s\S]+/}}],directive:{pattern:RegExp(/#/.source+"(?:"+/(?:elseif|if)\b/.source+"(?:[ 	]*"+/(?:![ \t]*)?(?:\b\w+\b(?:[ \t]*\((?:[^()]|\([^()]*\))*\))?|\((?:[^()]|\([^()]*\))*\))(?:[ \t]*(?:&&|\|\|))?/.source+")+|"+/(?:else|endif)\b/.source+")"),alias:"property",inside:{"directive-name":/^#\w+/,boolean:/\b(?:false|true)\b/,number:/\b\d+(?:\.\d+)*\b/,operator:/!|&&|\|\||[<>]=?/,punctuation:/[(),]/}},literal:{pattern:/#(?:colorLiteral|column|dsohandle|file(?:ID|Literal|Path)?|function|imageLiteral|line)\b/,alias:"constant"},"other-directive":{pattern:/#\w+\b/,alias:"property"},attribute:{pattern:/@\w+/,alias:"atrule"},"function-definition":{pattern:/(\bfunc\s+)\w+/,lookbehind:!0,alias:"function"},label:{pattern:/\b(break|continue)\s+\w+|\b[a-zA-Z_]\w*(?=\s*:\s*(?:for|repeat|while)\b)/,lookbehind:!0,alias:"important"},keyword:/\b(?:Any|Protocol|Self|Type|actor|as|assignment|associatedtype|associativity|async|await|break|case|catch|class|continue|convenience|default|defer|deinit|didSet|do|dynamic|else|enum|extension|fallthrough|fileprivate|final|for|func|get|guard|higherThan|if|import|in|indirect|infix|init|inout|internal|is|isolated|lazy|left|let|lowerThan|mutating|none|nonisolated|nonmutating|open|operator|optional|override|postfix|precedencegroup|prefix|private|protocol|public|repeat|required|rethrows|return|right|safe|self|set|some|static|struct|subscript|super|switch|throw|throws|try|typealias|unowned|unsafe|var|weak|where|while|willSet)\b/,boolean:/\b(?:false|true)\b/,nil:{pattern:/\bnil\b/,alias:"constant"},"short-argument":/\$\d+\b/,omit:{pattern:/\b_\b/,alias:"keyword"},number:/\b(?:[\d_]+(?:\.[\de_]+)?|0x[a-f0-9_]+(?:\.[a-f0-9p_]+)?|0b[01_]+|0o[0-7_]+)\b/i,"class-name":/\b[A-Z](?:[A-Z_\d]*[a-z]\w*)?\b/,function:/\b[a-z_]\w*(?=\s*\()/i,constant:/\b(?:[A-Z_]{2,}|k[A-Z][A-Za-z_]+)\b/,operator:/[-+*/%=!<>&|^~?]+|\.[.\-+*/%=!<>&|^~?]+/,punctuation:/[{}[\]();,.:\\]/},x.languages.swift["string-literal"].forEach(function(e){e.inside.interpolation.inside=x.languages.swift}),function(e){e.languages.kotlin=e.languages.extend("clike",{keyword:{pattern:/(^|[^.])\b(?:abstract|actual|annotation|as|break|by|catch|class|companion|const|constructor|continue|crossinline|data|do|dynamic|else|enum|expect|external|final|finally|for|fun|get|if|import|in|infix|init|inline|inner|interface|internal|is|lateinit|noinline|null|object|open|operator|out|override|package|private|protected|public|reified|return|sealed|set|super|suspend|tailrec|this|throw|to|try|typealias|val|var|vararg|when|where|while)\b/,lookbehind:!0},function:[{pattern:/(?:`[^\r\n`]+`|\b\w+)(?=\s*\()/,greedy:!0},{pattern:/(\.)(?:`[^\r\n`]+`|\w+)(?=\s*\{)/,lookbehind:!0,greedy:!0}],number:/\b(?:0[xX][\da-fA-F]+(?:_[\da-fA-F]+)*|0[bB][01]+(?:_[01]+)*|\d+(?:_\d+)*(?:\.\d+(?:_\d+)*)?(?:[eE][+-]?\d+(?:_\d+)*)?[fFL]?)\b/,operator:/\+[+=]?|-[-=>]?|==?=?|!(?:!|==?)?|[\/*%<>]=?|[?:]:?|\.\.|&&|\|\||\b(?:and|inv|or|shl|shr|ushr|xor)\b/}),delete e.languages.kotlin["class-name"];var n={"interpolation-punctuation":{pattern:/^\$\{?|\}$/,alias:"punctuation"},expression:{pattern:/[\s\S]+/,inside:e.languages.kotlin}};e.languages.insertBefore("kotlin","string",{"string-literal":[{pattern:/"""(?:[^$]|\$(?:(?!\{)|\{[^{}]*\}))*?"""/,alias:"multiline",inside:{interpolation:{pattern:/\$(?:[a-z_]\w*|\{[^{}]*\})/i,inside:n},string:/[\s\S]+/}},{pattern:/"(?:[^"\\\r\n$]|\\.|\$(?:(?!\{)|\{[^{}]*\}))*"/,alias:"singleline",inside:{interpolation:{pattern:/((?:^|[^\\])(?:\\{2})*)\$(?:[a-z_]\w*|\{[^{}]*\})/i,lookbehind:!0,inside:n},string:/[\s\S]+/}}],char:{pattern:/'(?:[^'\\\r\n]|\\(?:.|u[a-fA-F0-9]{0,4}))'/,greedy:!0}}),delete e.languages.kotlin.string,e.languages.insertBefore("kotlin","keyword",{annotation:{pattern:/\B@(?:\w+:)?(?:[A-Z]\w*|\[[^\]]+\])/,alias:"builtin"}}),e.languages.insertBefore("kotlin","function",{label:{pattern:/\b\w+@|@\w+\b/,alias:"symbol"}}),e.languages.kt=e.languages.kotlin,e.languages.kts=e.languages.kotlin}(x),x.languages.c=x.languages.extend("clike",{comment:{pattern:/\/\/(?:[^\r\n\\]|\\(?:\r\n?|\n|(?![\r\n])))*|\/\*[\s\S]*?(?:\*\/|$)/,greedy:!0},string:{pattern:/"(?:\\(?:\r\n|[\s\S])|[^"\\\r\n])*"/,greedy:!0},"class-name":{pattern:/(\b(?:enum|struct)\s+(?:__attribute__\s*\(\([\s\S]*?\)\)\s*)?)\w+|\b[a-z]\w*_t\b/,lookbehind:!0},keyword:/\b(?:_Alignas|_Alignof|_Atomic|_Bool|_Complex|_Generic|_Imaginary|_Noreturn|_Static_assert|_Thread_local|__attribute__|asm|auto|break|case|char|const|continue|default|do|double|else|enum|extern|float|for|goto|if|inline|int|long|register|return|short|signed|sizeof|static|struct|switch|typedef|typeof|union|unsigned|void|volatile|while)\b/,function:/\b[a-z_]\w*(?=\s*\()/i,number:/(?:\b0x(?:[\da-f]+(?:\.[\da-f]*)?|\.[\da-f]+)(?:p[+-]?\d+)?|(?:\b\d+(?:\.\d*)?|\B\.\d+)(?:e[+-]?\d+)?)[ful]{0,4}/i,operator:/>>=?|<<=?|->|([-+&|:])\1|[?:~]|[-+*/%&|^!=<>]=?/}),x.languages.insertBefore("c","string",{char:{pattern:/'(?:\\(?:\r\n|[\s\S])|[^'\\\r\n]){0,32}'/,greedy:!0}}),x.languages.insertBefore("c","string",{macro:{pattern:/(^[\t ]*)#\s*[a-z](?:[^\r\n\\/]|\/(?!\*)|\/\*(?:[^*]|\*(?!\/))*\*\/|\\(?:\r\n|[\s\S]))*/im,lookbehind:!0,greedy:!0,alias:"property",inside:{string:[{pattern:/^(#\s*include\s*)<[^>]+>/,lookbehind:!0},x.languages.c.string],char:x.languages.c.char,comment:x.languages.c.comment,"macro-name":[{pattern:/(^#\s*define\s+)\w+\b(?!\()/i,lookbehind:!0},{pattern:/(^#\s*define\s+)\w+\b(?=\()/i,lookbehind:!0,alias:"function"}],directive:{pattern:/^(#\s*)[a-z]+/,lookbehind:!0,alias:"keyword"},"directive-hash":/^#/,punctuation:/##|\\(?=[\r\n])/,expression:{pattern:/\S[\s\S]*/,inside:x.languages.c}}}}),x.languages.insertBefore("c","function",{constant:/\b(?:EOF|NULL|SEEK_CUR|SEEK_END|SEEK_SET|__DATE__|__FILE__|__LINE__|__TIMESTAMP__|__TIME__|__func__|stderr|stdin|stdout)\b/}),delete x.languages.c.boolean,x.languages.objectivec=x.languages.extend("c",{string:{pattern:/@?"(?:\\(?:\r\n|[\s\S])|[^"\\\r\n])*"/,greedy:!0},keyword:/\b(?:asm|auto|break|case|char|const|continue|default|do|double|else|enum|extern|float|for|goto|if|in|inline|int|long|register|return|self|short|signed|sizeof|static|struct|super|switch|typedef|typeof|union|unsigned|void|volatile|while)\b|(?:@interface|@end|@implementation|@protocol|@class|@public|@protected|@private|@property|@try|@catch|@finally|@throw|@synthesize|@dynamic|@selector)\b/,operator:/-[->]?|\+\+?|!=?|<<?=?|>>?=?|==?|&&?|\|\|?|[~^%?*\/@]/}),delete x.languages.objectivec["class-name"],x.languages.objc=x.languages.objectivec,x.languages.reason=x.languages.extend("clike",{string:{pattern:/"(?:\\(?:\r\n|[\s\S])|[^\\\r\n"])*"/,greedy:!0},"class-name":/\b[A-Z]\w*/,keyword:/\b(?:and|as|assert|begin|class|constraint|do|done|downto|else|end|exception|external|for|fun|function|functor|if|in|include|inherit|initializer|lazy|let|method|module|mutable|new|nonrec|object|of|open|or|private|rec|sig|struct|switch|then|to|try|type|val|virtual|when|while|with)\b/,operator:/\.{3}|:[:=]|\|>|->|=(?:==?|>)?|<=?|>=?|[|^?'#!~`]|[+\-*\/]\.?|\b(?:asr|land|lor|lsl|lsr|lxor|mod)\b/}),x.languages.insertBefore("reason","class-name",{char:{pattern:/'(?:\\x[\da-f]{2}|\\o[0-3][0-7][0-7]|\\\d{3}|\\.|[^'\\\r\n])'/,greedy:!0},constructor:/\b[A-Z]\w*\b(?!\s*\.)/,label:{pattern:/\b[a-z]\w*(?=::)/,alias:"symbol"}}),delete x.languages.reason.function,function(e){for(var n=/\/\*(?:[^*/]|\*(?!\/)|\/(?!\*)|<self>)*\*\//.source,t=0;t<2;t++)n=n.replace(/<self>/g,function(){return n});n=n.replace(/<self>/g,function(){return/[^\s\S]/.source}),e.languages.rust={comment:[{pattern:RegExp(/(^|[^\\])/.source+n),lookbehind:!0,greedy:!0},{pattern:/(^|[^\\:])\/\/.*/,lookbehind:!0,greedy:!0}],string:{pattern:/b?"(?:\\[\s\S]|[^\\"])*"|b?r(#*)"(?:[^"]|"(?!\1))*"\1/,greedy:!0},char:{pattern:/b?'(?:\\(?:x[0-7][\da-fA-F]|u\{(?:[\da-fA-F]_*){1,6}\}|.)|[^\\\r\n\t'])'/,greedy:!0},attribute:{pattern:/#!?\[(?:[^\[\]"]|"(?:\\[\s\S]|[^\\"])*")*\]/,greedy:!0,alias:"attr-name",inside:{string:null}},"closure-params":{pattern:/([=(,:]\s*|\bmove\s*)\|[^|]*\||\|[^|]*\|(?=\s*(?:\{|->))/,lookbehind:!0,greedy:!0,inside:{"closure-punctuation":{pattern:/^\||\|$/,alias:"punctuation"},rest:null}},"lifetime-annotation":{pattern:/'\w+/,alias:"symbol"},"fragment-specifier":{pattern:/(\$\w+:)[a-z]+/,lookbehind:!0,alias:"punctuation"},variable:/\$\w+/,"function-definition":{pattern:/(\bfn\s+)\w+/,lookbehind:!0,alias:"function"},"type-definition":{pattern:/(\b(?:enum|struct|trait|type|union)\s+)\w+/,lookbehind:!0,alias:"class-name"},"module-declaration":[{pattern:/(\b(?:crate|mod)\s+)[a-z][a-z_\d]*/,lookbehind:!0,alias:"namespace"},{pattern:/(\b(?:crate|self|super)\s*)::\s*[a-z][a-z_\d]*\b(?:\s*::(?:\s*[a-z][a-z_\d]*\s*::)*)?/,lookbehind:!0,alias:"namespace",inside:{punctuation:/::/}}],keyword:[/\b(?:Self|abstract|as|async|await|become|box|break|const|continue|crate|do|dyn|else|enum|extern|final|fn|for|if|impl|in|let|loop|macro|match|mod|move|mut|override|priv|pub|ref|return|self|static|struct|super|trait|try|type|typeof|union|unsafe|unsized|use|virtual|where|while|yield)\b/,/\b(?:bool|char|f(?:32|64)|[ui](?:8|16|32|64|128|size)|str)\b/],function:/\b[a-z_]\w*(?=\s*(?:::\s*<|\())/,macro:{pattern:/\b\w+!/,alias:"property"},constant:/\b[A-Z_][A-Z_\d]+\b/,"class-name":/\b[A-Z]\w*\b/,namespace:{pattern:/(?:\b[a-z][a-z_\d]*\s*::\s*)*\b[a-z][a-z_\d]*\s*::(?!\s*<)/,inside:{punctuation:/::/}},number:/\b(?:0x[\dA-Fa-f](?:_?[\dA-Fa-f])*|0o[0-7](?:_?[0-7])*|0b[01](?:_?[01])*|(?:(?:\d(?:_?\d)*)?\.)?\d(?:_?\d)*(?:[Ee][+-]?\d+)?)(?:_?(?:f32|f64|[iu](?:8|16|32|64|size)?))?\b/,boolean:/\b(?:false|true)\b/,punctuation:/->|\.\.=|\.{1,3}|::|[{}[\];(),:]/,operator:/[-+*\/%!^]=?|=[=>]?|&[&=]?|\|[|=]?|<<?=?|>>?=?|[@?]/},e.languages.rust["closure-params"].inside.rest=e.languages.rust,e.languages.rust.attribute.inside.string=e.languages.rust.string}(x),x.languages.go=x.languages.extend("clike",{string:{pattern:/(^|[^\\])"(?:\\.|[^"\\\r\n])*"|`[^`]*`/,lookbehind:!0,greedy:!0},keyword:/\b(?:break|case|chan|const|continue|default|defer|else|fallthrough|for|func|go(?:to)?|if|import|interface|map|package|range|return|select|struct|switch|type|var)\b/,boolean:/\b(?:_|false|iota|nil|true)\b/,number:[/\b0(?:b[01_]+|o[0-7_]+)i?\b/i,/\b0x(?:[a-f\d_]+(?:\.[a-f\d_]*)?|\.[a-f\d_]+)(?:p[+-]?\d+(?:_\d+)*)?i?(?!\w)/i,/(?:\b\d[\d_]*(?:\.[\d_]*)?|\B\.\d[\d_]*)(?:e[+-]?[\d_]+)?i?(?!\w)/i],operator:/[*\/%^!=]=?|\+[=+]?|-[=-]?|\|[=|]?|&(?:=|&|\^=?)?|>(?:>=?|=)?|<(?:<=?|=|-)?|:=|\.\.\./,builtin:/\b(?:append|bool|byte|cap|close|complex|complex(?:64|128)|copy|delete|error|float(?:32|64)|u?int(?:8|16|32|64)?|imag|len|make|new|panic|print(?:ln)?|real|recover|rune|string|uintptr)\b/}),x.languages.insertBefore("go","string",{char:{pattern:/'(?:\\.|[^'\\\r\n]){0,10}'/,greedy:!0}}),delete x.languages.go["class-name"],function(e){var n=/\b(?:alignas|alignof|asm|auto|bool|break|case|catch|char|char16_t|char32_t|char8_t|class|co_await|co_return|co_yield|compl|concept|const|const_cast|consteval|constexpr|constinit|continue|decltype|default|delete|do|double|dynamic_cast|else|enum|explicit|export|extern|final|float|for|friend|goto|if|import|inline|int|int16_t|int32_t|int64_t|int8_t|long|module|mutable|namespace|new|noexcept|nullptr|operator|override|private|protected|public|register|reinterpret_cast|requires|return|short|signed|sizeof|static|static_assert|static_cast|struct|switch|template|this|thread_local|throw|try|typedef|typeid|typename|uint16_t|uint32_t|uint64_t|uint8_t|union|unsigned|using|virtual|void|volatile|wchar_t|while)\b/,t=/\b(?!<keyword>)\w+(?:\s*\.\s*\w+)*\b/.source.replace(/<keyword>/g,function(){return n.source});e.languages.cpp=e.languages.extend("c",{"class-name":[{pattern:RegExp(/(\b(?:class|concept|enum|struct|typename)\s+)(?!<keyword>)\w+/.source.replace(/<keyword>/g,function(){return n.source})),lookbehind:!0},/\b[A-Z]\w*(?=\s*::\s*\w+\s*\()/,/\b[A-Z_]\w*(?=\s*::\s*~\w+\s*\()/i,/\b\w+(?=\s*<(?:[^<>]|<(?:[^<>]|<[^<>]*>)*>)*>\s*::\s*\w+\s*\()/],keyword:n,number:{pattern:/(?:\b0b[01']+|\b0x(?:[\da-f']+(?:\.[\da-f']*)?|\.[\da-f']+)(?:p[+-]?[\d']+)?|(?:\b[\d']+(?:\.[\d']*)?|\B\.[\d']+)(?:e[+-]?[\d']+)?)[ful]{0,4}/i,greedy:!0},operator:/>>=?|<<=?|->|--|\+\+|&&|\|\||[?:~]|<=>|[-+*/%&|^!=<>]=?|\b(?:and|and_eq|bitand|bitor|not|not_eq|or|or_eq|xor|xor_eq)\b/,boolean:/\b(?:false|true)\b/}),e.languages.insertBefore("cpp","string",{module:{pattern:RegExp(/(\b(?:import|module)\s+)/.source+"(?:"+/"(?:\\(?:\r\n|[\s\S])|[^"\\\r\n])*"|<[^<>\r\n]*>/.source+"|"+/<mod-name>(?:\s*:\s*<mod-name>)?|:\s*<mod-name>/.source.replace(/<mod-name>/g,function(){return t})+")"),lookbehind:!0,greedy:!0,inside:{string:/^[<"][\s\S]+/,operator:/:/,punctuation:/\./}},"raw-string":{pattern:/R"([^()\\ ]{0,16})\([\s\S]*?\)\1"/,alias:"string",greedy:!0}}),e.languages.insertBefore("cpp","keyword",{"generic-function":{pattern:/\b(?!operator\b)[a-z_]\w*\s*<(?:[^<>]|<[^<>]*>)*>(?=\s*\()/i,inside:{function:/^\w+/,generic:{pattern:/<[\s\S]+/,alias:"class-name",inside:e.languages.cpp}}}}),e.languages.insertBefore("cpp","operator",{"double-colon":{pattern:/::/,alias:"punctuation"}}),e.languages.insertBefore("cpp","class-name",{"base-clause":{pattern:/(\b(?:class|struct)\s+\w+\s*:\s*)[^;{}"'\s]+(?:\s+[^;{}"'\s]+)*(?=\s*[;{])/,lookbehind:!0,greedy:!0,inside:e.languages.extend("cpp",{})}}),e.languages.insertBefore("inside","double-colon",{"class-name":/\b[a-z_]\w*\b(?!\s*::)/i},e.languages.cpp["base-clause"])}(x),x.languages.python={comment:{pattern:/(^|[^\\])#.*/,lookbehind:!0,greedy:!0},"string-interpolation":{pattern:/(?:f|fr|rf)(?:("""|''')[\s\S]*?\1|("|')(?:\\.|(?!\2)[^\\\r\n])*\2)/i,greedy:!0,inside:{interpolation:{pattern:/((?:^|[^{])(?:\{\{)*)\{(?!\{)(?:[^{}]|\{(?!\{)(?:[^{}]|\{(?!\{)(?:[^{}])+\})+\})+\}/,lookbehind:!0,inside:{"format-spec":{pattern:/(:)[^:(){}]+(?=\}$)/,lookbehind:!0},"conversion-option":{pattern:/![sra](?=[:}]$)/,alias:"punctuation"},rest:null}},string:/[\s\S]+/}},"triple-quoted-string":{pattern:/(?:[rub]|br|rb)?("""|''')[\s\S]*?\1/i,greedy:!0,alias:"string"},string:{pattern:/(?:[rub]|br|rb)?("|')(?:\\.|(?!\1)[^\\\r\n])*\1/i,greedy:!0},function:{pattern:/((?:^|\s)def[ \t]+)[a-zA-Z_]\w*(?=\s*\()/g,lookbehind:!0},"class-name":{pattern:/(\bclass\s+)\w+/i,lookbehind:!0},decorator:{pattern:/(^[\t ]*)@\w+(?:\.\w+)*/m,lookbehind:!0,alias:["annotation","punctuation"],inside:{punctuation:/\./}},keyword:/\b(?:_(?=\s*:)|and|as|assert|async|await|break|case|class|continue|def|del|elif|else|except|exec|finally|for|from|global|if|import|in|is|lambda|match|nonlocal|not|or|pass|print|raise|return|try|while|with|yield)\b/,builtin:/\b(?:__import__|abs|all|any|apply|ascii|basestring|bin|bool|buffer|bytearray|bytes|callable|chr|classmethod|cmp|coerce|compile|complex|delattr|dict|dir|divmod|enumerate|eval|execfile|file|filter|float|format|frozenset|getattr|globals|hasattr|hash|help|hex|id|input|int|intern|isinstance|issubclass|iter|len|list|locals|long|map|max|memoryview|min|next|object|oct|open|ord|pow|property|range|raw_input|reduce|reload|repr|reversed|round|set|setattr|slice|sorted|staticmethod|str|sum|super|tuple|type|unichr|unicode|vars|xrange|zip)\b/,boolean:/\b(?:False|None|True)\b/,number:/\b0(?:b(?:_?[01])+|o(?:_?[0-7])+|x(?:_?[a-f0-9])+)\b|(?:\b\d+(?:_\d+)*(?:\.(?:\d+(?:_\d+)*)?)?|\B\.\d+(?:_\d+)*)(?:e[+-]?\d+(?:_\d+)*)?j?(?!\w)/i,operator:/[-+%=]=?|!=|:=|\*\*?=?|\/\/?=?|<[<=>]?|>[=>]?|[&|^~]/,punctuation:/[{}[\];(),.:]/},x.languages.python["string-interpolation"].inside.interpolation.inside.rest=x.languages.python,x.languages.py=x.languages.python;var Nc={};yf(Nc,{dracula:()=>xf,duotoneDark:()=>kf,duotoneLight:()=>Sf,github:()=>Cf,jettwaveDark:()=>Wf,jettwaveLight:()=>Yf,nightOwl:()=>Rf,nightOwlLight:()=>Af,oceanicNext:()=>If,okaidia:()=>Of,oneDark:()=>Zf,oneLight:()=>Jf,palenight:()=>Lf,shadesOfPurple:()=>Df,synthwave84:()=>Uf,ultramin:()=>$f,vsDark:()=>Rc,vsLight:()=>Vf});var vf={plain:{color:"#F8F8F2",backgroundColor:"#282A36"},styles:[{types:["prolog","constant","builtin"],style:{color:"rgb(189, 147, 249)"}},{types:["inserted","function"],style:{color:"rgb(80, 250, 123)"}},{types:["deleted"],style:{color:"rgb(255, 85, 85)"}},{types:["changed"],style:{color:"rgb(255, 184, 108)"}},{types:["punctuation","symbol"],style:{color:"rgb(248, 248, 242)"}},{types:["string","char","tag","selector"],style:{color:"rgb(255, 121, 198)"}},{types:["keyword","variable"],style:{color:"rgb(189, 147, 249)",fontStyle:"italic"}},{types:["comment"],style:{color:"rgb(98, 114, 164)"}},{types:["attr-name"],style:{color:"rgb(241, 250, 140)"}}]},xf=vf,wf={plain:{backgroundColor:"#2a2734",color:"#9a86fd"},styles:[{types:["comment","prolog","doctype","cdata","punctuation"],style:{color:"#6c6783"}},{types:["namespace"],style:{opacity:.7}},{types:["tag","operator","number"],style:{color:"#e09142"}},{types:["property","function"],style:{color:"#9a86fd"}},{types:["tag-id","selector","atrule-id"],style:{color:"#eeebff"}},{types:["attr-name"],style:{color:"#c4b9fe"}},{types:["boolean","string","entity","url","attr-value","keyword","control","directive","unit","statement","regex","atrule","placeholder","variable"],style:{color:"#ffcc99"}},{types:["deleted"],style:{textDecorationLine:"line-through"}},{types:["inserted"],style:{textDecorationLine:"underline"}},{types:["italic"],style:{fontStyle:"italic"}},{types:["important","bold"],style:{fontWeight:"bold"}},{types:["important"],style:{color:"#c4b9fe"}}]},kf=wf,Ef={plain:{backgroundColor:"#faf8f5",color:"#728fcb"},styles:[{types:["comment","prolog","doctype","cdata","punctuation"],style:{color:"#b6ad9a"}},{types:["namespace"],style:{opacity:.7}},{types:["tag","operator","number"],style:{color:"#063289"}},{types:["property","function"],style:{color:"#b29762"}},{types:["tag-id","selector","atrule-id"],style:{color:"#2d2006"}},{types:["attr-name"],style:{color:"#896724"}},{types:["boolean","string","entity","url","attr-value","keyword","control","directive","unit","statement","regex","atrule"],style:{color:"#728fcb"}},{types:["placeholder","variable"],style:{color:"#93abdc"}},{types:["deleted"],style:{textDecorationLine:"line-through"}},{types:["inserted"],style:{textDecorationLine:"underline"}},{types:["italic"],style:{fontStyle:"italic"}},{types:["important","bold"],style:{fontWeight:"bold"}},{types:["important"],style:{color:"#896724"}}]},Sf=Ef,bf={plain:{color:"#393A34",backgroundColor:"#f6f8fa"},styles:[{types:["comment","prolog","doctype","cdata"],style:{color:"#999988",fontStyle:"italic"}},{types:["namespace"],style:{opacity:.7}},{types:["string","attr-value"],style:{color:"#e3116c"}},{types:["punctuation","operator"],style:{color:"#393A34"}},{types:["entity","url","symbol","number","boolean","variable","constant","property","regex","inserted"],style:{color:"#36acaa"}},{types:["atrule","keyword","attr-name","selector"],style:{color:"#00a4db"}},{types:["function","deleted","tag"],style:{color:"#d73a49"}},{types:["function-variable"],style:{color:"#6f42c1"}},{types:["tag","selector","keyword"],style:{color:"#00009f"}}]},Cf=bf,Nf={plain:{color:"#d6deeb",backgroundColor:"#011627"},styles:[{types:["changed"],style:{color:"rgb(162, 191, 252)",fontStyle:"italic"}},{types:["deleted"],style:{color:"rgba(239, 83, 80, 0.56)",fontStyle:"italic"}},{types:["inserted","attr-name"],style:{color:"rgb(173, 219, 103)",fontStyle:"italic"}},{types:["comment"],style:{color:"rgb(99, 119, 119)",fontStyle:"italic"}},{types:["string","url"],style:{color:"rgb(173, 219, 103)"}},{types:["variable"],style:{color:"rgb(214, 222, 235)"}},{types:["number"],style:{color:"rgb(247, 140, 108)"}},{types:["builtin","char","constant","function"],style:{color:"rgb(130, 170, 255)"}},{types:["punctuation"],style:{color:"rgb(199, 146, 234)"}},{types:["selector","doctype"],style:{color:"rgb(199, 146, 234)",fontStyle:"italic"}},{types:["class-name"],style:{color:"rgb(255, 203, 139)"}},{types:["tag","operator","keyword"],style:{color:"rgb(127, 219, 202)"}},{types:["boolean"],style:{color:"rgb(255, 88, 116)"}},{types:["property"],style:{color:"rgb(128, 203, 196)"}},{types:["namespace"],style:{color:"rgb(178, 204, 214)"}}]},Rf=Nf,Tf={plain:{color:"#403f53",backgroundColor:"#FBFBFB"},styles:[{types:["changed"],style:{color:"rgb(162, 191, 252)",fontStyle:"italic"}},{types:["deleted"],style:{color:"rgba(239, 83, 80, 0.56)",fontStyle:"italic"}},{types:["inserted","attr-name"],style:{color:"rgb(72, 118, 214)",fontStyle:"italic"}},{types:["comment"],style:{color:"rgb(152, 159, 177)",fontStyle:"italic"}},{types:["string","builtin","char","constant","url"],style:{color:"rgb(72, 118, 214)"}},{types:["variable"],style:{color:"rgb(201, 103, 101)"}},{types:["number"],style:{color:"rgb(170, 9, 130)"}},{types:["punctuation"],style:{color:"rgb(153, 76, 195)"}},{types:["function","selector","doctype"],style:{color:"rgb(153, 76, 195)",fontStyle:"italic"}},{types:["class-name"],style:{color:"rgb(17, 17, 17)"}},{types:["tag"],style:{color:"rgb(153, 76, 195)"}},{types:["operator","property","keyword","namespace"],style:{color:"rgb(12, 150, 155)"}},{types:["boolean"],style:{color:"rgb(188, 84, 84)"}}]},Af=Tf,ve={char:"#D8DEE9",comment:"#999999",keyword:"#c5a5c5",primitive:"#5a9bcf",string:"#8dc891",variable:"#d7deea",boolean:"#ff8b50",punctuation:"#5FB3B3",tag:"#fc929e",function:"#79b6f2",className:"#FAC863",method:"#6699CC",operator:"#fc929e"},Pf={plain:{backgroundColor:"#282c34",color:"#ffffff"},styles:[{types:["attr-name"],style:{color:ve.keyword}},{types:["attr-value"],style:{color:ve.string}},{types:["comment","block-comment","prolog","doctype","cdata","shebang"],style:{color:ve.comment}},{types:["property","number","function-name","constant","symbol","deleted"],style:{color:ve.primitive}},{types:["boolean"],style:{color:ve.boolean}},{types:["tag"],style:{color:ve.tag}},{types:["string"],style:{color:ve.string}},{types:["punctuation"],style:{color:ve.string}},{types:["selector","char","builtin","inserted"],style:{color:ve.char}},{types:["function"],style:{color:ve.function}},{types:["operator","entity","url","variable"],style:{color:ve.variable}},{types:["keyword"],style:{color:ve.keyword}},{types:["atrule","class-name"],style:{color:ve.className}},{types:["important"],style:{fontWeight:"400"}},{types:["bold"],style:{fontWeight:"bold"}},{types:["italic"],style:{fontStyle:"italic"}},{types:["namespace"],style:{opacity:.7}}]},If=Pf,Ff={plain:{color:"#f8f8f2",backgroundColor:"#272822"},styles:[{types:["changed"],style:{color:"rgb(162, 191, 252)",fontStyle:"italic"}},{types:["deleted"],style:{color:"#f92672",fontStyle:"italic"}},{types:["inserted"],style:{color:"rgb(173, 219, 103)",fontStyle:"italic"}},{types:["comment"],style:{color:"#8292a2",fontStyle:"italic"}},{types:["string","url"],style:{color:"#a6e22e"}},{types:["variable"],style:{color:"#f8f8f2"}},{types:["number"],style:{color:"#ae81ff"}},{types:["builtin","char","constant","function","class-name"],style:{color:"#e6db74"}},{types:["punctuation"],style:{color:"#f8f8f2"}},{types:["selector","doctype"],style:{color:"#a6e22e",fontStyle:"italic"}},{types:["tag","operator","keyword"],style:{color:"#66d9ef"}},{types:["boolean"],style:{color:"#ae81ff"}},{types:["namespace"],style:{color:"rgb(178, 204, 214)",opacity:.7}},{types:["tag","property"],style:{color:"#f92672"}},{types:["attr-name"],style:{color:"#a6e22e !important"}},{types:["doctype"],style:{color:"#8292a2"}},{types:["rule"],style:{color:"#e6db74"}}]},Of=Ff,Mf={plain:{color:"#bfc7d5",backgroundColor:"#292d3e"},styles:[{types:["comment"],style:{color:"rgb(105, 112, 152)",fontStyle:"italic"}},{types:["string","inserted"],style:{color:"rgb(195, 232, 141)"}},{types:["number"],style:{color:"rgb(247, 140, 108)"}},{types:["builtin","char","constant","function"],style:{color:"rgb(130, 170, 255)"}},{types:["punctuation","selector"],style:{color:"rgb(199, 146, 234)"}},{types:["variable"],style:{color:"rgb(191, 199, 213)"}},{types:["class-name","attr-name"],style:{color:"rgb(255, 203, 107)"}},{types:["tag","deleted"],style:{color:"rgb(255, 85, 114)"}},{types:["operator"],style:{color:"rgb(137, 221, 255)"}},{types:["boolean"],style:{color:"rgb(255, 88, 116)"}},{types:["keyword"],style:{fontStyle:"italic"}},{types:["doctype"],style:{color:"rgb(199, 146, 234)",fontStyle:"italic"}},{types:["namespace"],style:{color:"rgb(178, 204, 214)"}},{types:["url"],style:{color:"rgb(221, 221, 221)"}}]},Lf=Mf,jf={plain:{color:"#9EFEFF",backgroundColor:"#2D2A55"},styles:[{types:["changed"],style:{color:"rgb(255, 238, 128)"}},{types:["deleted"],style:{color:"rgba(239, 83, 80, 0.56)"}},{types:["inserted"],style:{color:"rgb(173, 219, 103)"}},{types:["comment"],style:{color:"rgb(179, 98, 255)",fontStyle:"italic"}},{types:["punctuation"],style:{color:"rgb(255, 255, 255)"}},{types:["constant"],style:{color:"rgb(255, 98, 140)"}},{types:["string","url"],style:{color:"rgb(165, 255, 144)"}},{types:["variable"],style:{color:"rgb(255, 238, 128)"}},{types:["number","boolean"],style:{color:"rgb(255, 98, 140)"}},{types:["attr-name"],style:{color:"rgb(255, 180, 84)"}},{types:["keyword","operator","property","namespace","tag","selector","doctype"],style:{color:"rgb(255, 157, 0)"}},{types:["builtin","char","constant","function","class-name"],style:{color:"rgb(250, 208, 0)"}}]},Df=jf,zf={plain:{backgroundColor:"linear-gradient(to bottom, #2a2139 75%, #34294f)",backgroundImage:"#34294f",color:"#f92aad",textShadow:"0 0 2px #100c0f, 0 0 5px #dc078e33, 0 0 10px #fff3"},styles:[{types:["comment","block-comment","prolog","doctype","cdata"],style:{color:"#495495",fontStyle:"italic"}},{types:["punctuation"],style:{color:"#ccc"}},{types:["tag","attr-name","namespace","number","unit","hexcode","deleted"],style:{color:"#e2777a"}},{types:["property","selector"],style:{color:"#72f1b8",textShadow:"0 0 2px #100c0f, 0 0 10px #257c5575, 0 0 35px #21272475"}},{types:["function-name"],style:{color:"#6196cc"}},{types:["boolean","selector-id","function"],style:{color:"#fdfdfd",textShadow:"0 0 2px #001716, 0 0 3px #03edf975, 0 0 5px #03edf975, 0 0 8px #03edf975"}},{types:["class-name","maybe-class-name","builtin"],style:{color:"#fff5f6",textShadow:"0 0 2px #000, 0 0 10px #fc1f2c75, 0 0 5px #fc1f2c75, 0 0 25px #fc1f2c75"}},{types:["constant","symbol"],style:{color:"#f92aad",textShadow:"0 0 2px #100c0f, 0 0 5px #dc078e33, 0 0 10px #fff3"}},{types:["important","atrule","keyword","selector-class"],style:{color:"#f4eee4",textShadow:"0 0 2px #393a33, 0 0 8px #f39f0575, 0 0 2px #f39f0575"}},{types:["string","char","attr-value","regex","variable"],style:{color:"#f87c32"}},{types:["parameter"],style:{fontStyle:"italic"}},{types:["entity","url"],style:{color:"#67cdcc"}},{types:["operator"],style:{color:"ffffffee"}},{types:["important","bold"],style:{fontWeight:"bold"}},{types:["italic"],style:{fontStyle:"italic"}},{types:["entity"],style:{cursor:"help"}},{types:["inserted"],style:{color:"green"}}]},Uf=zf,Bf={plain:{color:"#282a2e",backgroundColor:"#ffffff"},styles:[{types:["comment"],style:{color:"rgb(197, 200, 198)"}},{types:["string","number","builtin","variable"],style:{color:"rgb(150, 152, 150)"}},{types:["class-name","function","tag","attr-name"],style:{color:"rgb(40, 42, 46)"}}]},$f=Bf,Hf={plain:{color:"#9CDCFE",backgroundColor:"#1E1E1E"},styles:[{types:["prolog"],style:{color:"rgb(0, 0, 128)"}},{types:["comment"],style:{color:"rgb(106, 153, 85)"}},{types:["builtin","changed","keyword","interpolation-punctuation"],style:{color:"rgb(86, 156, 214)"}},{types:["number","inserted"],style:{color:"rgb(181, 206, 168)"}},{types:["constant"],style:{color:"rgb(100, 102, 149)"}},{types:["attr-name","variable"],style:{color:"rgb(156, 220, 254)"}},{types:["deleted","string","attr-value","template-punctuation"],style:{color:"rgb(206, 145, 120)"}},{types:["selector"],style:{color:"rgb(215, 186, 125)"}},{types:["tag"],style:{color:"rgb(78, 201, 176)"}},{types:["tag"],languages:["markup"],style:{color:"rgb(86, 156, 214)"}},{types:["punctuation","operator"],style:{color:"rgb(212, 212, 212)"}},{types:["punctuation"],languages:["markup"],style:{color:"#808080"}},{types:["function"],style:{color:"rgb(220, 220, 170)"}},{types:["class-name"],style:{color:"rgb(78, 201, 176)"}},{types:["char"],style:{color:"rgb(209, 105, 105)"}}]},Rc=Hf,qf={plain:{color:"#000000",backgroundColor:"#ffffff"},styles:[{types:["comment"],style:{color:"rgb(0, 128, 0)"}},{types:["builtin"],style:{color:"rgb(0, 112, 193)"}},{types:["number","variable","inserted"],style:{color:"rgb(9, 134, 88)"}},{types:["operator"],style:{color:"rgb(0, 0, 0)"}},{types:["constant","char"],style:{color:"rgb(129, 31, 63)"}},{types:["tag"],style:{color:"rgb(128, 0, 0)"}},{types:["attr-name"],style:{color:"rgb(255, 0, 0)"}},{types:["deleted","string"],style:{color:"rgb(163, 21, 21)"}},{types:["changed","punctuation"],style:{color:"rgb(4, 81, 165)"}},{types:["function","keyword"],style:{color:"rgb(0, 0, 255)"}},{types:["class-name"],style:{color:"rgb(38, 127, 153)"}}]},Vf=qf,Gf={plain:{color:"#f8fafc",backgroundColor:"#011627"},styles:[{types:["prolog"],style:{color:"#000080"}},{types:["comment"],style:{color:"#6A9955"}},{types:["builtin","changed","keyword","interpolation-punctuation"],style:{color:"#569CD6"}},{types:["number","inserted"],style:{color:"#B5CEA8"}},{types:["constant"],style:{color:"#f8fafc"}},{types:["attr-name","variable"],style:{color:"#9CDCFE"}},{types:["deleted","string","attr-value","template-punctuation"],style:{color:"#cbd5e1"}},{types:["selector"],style:{color:"#D7BA7D"}},{types:["tag"],style:{color:"#0ea5e9"}},{types:["tag"],languages:["markup"],style:{color:"#0ea5e9"}},{types:["punctuation","operator"],style:{color:"#D4D4D4"}},{types:["punctuation"],languages:["markup"],style:{color:"#808080"}},{types:["function"],style:{color:"#7dd3fc"}},{types:["class-name"],style:{color:"#0ea5e9"}},{types:["char"],style:{color:"#D16969"}}]},Wf=Gf,Kf={plain:{color:"#0f172a",backgroundColor:"#f1f5f9"},styles:[{types:["prolog"],style:{color:"#000080"}},{types:["comment"],style:{color:"#6A9955"}},{types:["builtin","changed","keyword","interpolation-punctuation"],style:{color:"#0c4a6e"}},{types:["number","inserted"],style:{color:"#B5CEA8"}},{types:["constant"],style:{color:"#0f172a"}},{types:["attr-name","variable"],style:{color:"#0c4a6e"}},{types:["deleted","string","attr-value","template-punctuation"],style:{color:"#64748b"}},{types:["selector"],style:{color:"#D7BA7D"}},{types:["tag"],style:{color:"#0ea5e9"}},{types:["tag"],languages:["markup"],style:{color:"#0ea5e9"}},{types:["punctuation","operator"],style:{color:"#475569"}},{types:["punctuation"],languages:["markup"],style:{color:"#808080"}},{types:["function"],style:{color:"#0e7490"}},{types:["class-name"],style:{color:"#0ea5e9"}},{types:["char"],style:{color:"#D16969"}}]},Yf=Kf,Qf={plain:{backgroundColor:"hsl(220, 13%, 18%)",color:"hsl(220, 14%, 71%)",textShadow:"0 1px rgba(0, 0, 0, 0.3)"},styles:[{types:["comment","prolog","cdata"],style:{color:"hsl(220, 10%, 40%)"}},{types:["doctype","punctuation","entity"],style:{color:"hsl(220, 14%, 71%)"}},{types:["attr-name","class-name","maybe-class-name","boolean","constant","number","atrule"],style:{color:"hsl(29, 54%, 61%)"}},{types:["keyword"],style:{color:"hsl(286, 60%, 67%)"}},{types:["property","tag","symbol","deleted","important"],style:{color:"hsl(355, 65%, 65%)"}},{types:["selector","string","char","builtin","inserted","regex","attr-value"],style:{color:"hsl(95, 38%, 62%)"}},{types:["variable","operator","function"],style:{color:"hsl(207, 82%, 66%)"}},{types:["url"],style:{color:"hsl(187, 47%, 55%)"}},{types:["deleted"],style:{textDecorationLine:"line-through"}},{types:["inserted"],style:{textDecorationLine:"underline"}},{types:["italic"],style:{fontStyle:"italic"}},{types:["important","bold"],style:{fontWeight:"bold"}},{types:["important"],style:{color:"hsl(220, 14%, 71%)"}}]},Zf=Qf,Xf={plain:{backgroundColor:"hsl(230, 1%, 98%)",color:"hsl(230, 8%, 24%)"},styles:[{types:["comment","prolog","cdata"],style:{color:"hsl(230, 4%, 64%)"}},{types:["doctype","punctuation","entity"],style:{color:"hsl(230, 8%, 24%)"}},{types:["attr-name","class-name","boolean","constant","number","atrule"],style:{color:"hsl(35, 99%, 36%)"}},{types:["keyword"],style:{color:"hsl(301, 63%, 40%)"}},{types:["property","tag","symbol","deleted","important"],style:{color:"hsl(5, 74%, 59%)"}},{types:["selector","string","char","builtin","inserted","regex","attr-value","punctuation"],style:{color:"hsl(119, 34%, 47%)"}},{types:["variable","operator","function"],style:{color:"hsl(221, 87%, 60%)"}},{types:["url"],style:{color:"hsl(198, 99%, 37%)"}},{types:["deleted"],style:{textDecorationLine:"line-through"}},{types:["inserted"],style:{textDecorationLine:"underline"}},{types:["italic"],style:{fontStyle:"italic"}},{types:["important","bold"],style:{fontWeight:"bold"}},{types:["important"],style:{color:"hsl(230, 8%, 24%)"}}]},Jf=Xf,em=(e,n)=>{const{plain:t}=e,r=e.styles.reduce((o,i)=>{const{languages:a,style:s}=i;return a&&!a.includes(n)||i.types.forEach(l=>{const p=Ye(Ye({},o[l]),s);o[l]=p}),o},{});return r.root=t,r.plain=Po(Ye({},t),{backgroundColor:void 0}),r},ol=em,nm=(e,n)=>{const[t,r]=z.useState(ol(n,e)),o=z.useRef(),i=z.useRef();return z.useEffect(()=>{(n!==o.current||e!==i.current)&&(o.current=n,i.current=e,r(ol(n,e)))},[e,n]),t},tm=e=>z.useCallback(n=>{var t=n,{className:r,style:o,line:i}=t,a=Cc(t,["className","style","line"]);const s=Po(Ye({},a),{className:Ec("token-line",r)});return typeof e=="object"&&"plain"in e&&(s.style=e.plain),typeof o=="object"&&(s.style=Ye(Ye({},s.style||{}),o)),s},[e]),rm=e=>{const n=z.useCallback(({types:t,empty:r})=>{if(e!=null){{if(t.length===1&&t[0]==="plain")return r!=null?{display:"inline-block"}:void 0;if(t.length===1&&r!=null)return e[t[0]]}return Object.assign(r!=null?{display:"inline-block"}:{},...t.map(o=>e[o]))}},[e]);return z.useCallback(t=>{var r=t,{token:o,className:i,style:a}=r,s=Cc(r,["token","className","style"]);const l=Po(Ye({},s),{className:Ec("token",...o.types,i),children:o.content,style:n(o)});return a!=null&&(l.style=Ye(Ye({},l.style||{}),a)),l},[n])},om=/\r\n|\r|\n/,il=e=>{e.length===0?e.push({types:["plain"],content:`
`,empty:!0}):e.length===1&&e[0].content===""&&(e[0].content=`
`,e[0].empty=!0)},al=(e,n)=>{const t=e.length;return t>0&&e[t-1]===n?e:e.concat(n)},im=e=>{const n=[[]],t=[e],r=[0],o=[e.length];let i=0,a=0,s=[];const l=[s];for(;a>-1;){for(;(i=r[a]++)<o[a];){let p,g=n[a];const _=t[a][i];if(typeof _=="string"?(g=a>0?g:["plain"],p=_):(g=al(g,_.type),_.alias&&(g=al(g,_.alias)),p=_.content),typeof p!="string"){a++,n.push(g),t.push(p),r.push(0),o.push(p.length);continue}const w=p.split(om),f=w.length;s.push({types:g,content:w[0]});for(let m=1;m<f;m++)il(s),l.push(s=[]),s.push({types:g,content:w[m]})}a--,n.pop(),t.pop(),r.pop(),o.pop()}return il(s),l},sl=im,am=({prism:e,code:n,grammar:t,language:r})=>{const o=z.useRef(e);return z.useMemo(()=>{if(t==null)return sl([n]);const i={code:n,grammar:t,language:r,tokens:[]};return o.current.hooks.run("before-tokenize",i),i.tokens=o.current.tokenize(n,t),o.current.hooks.run("after-tokenize",i),sl(i.tokens)},[n,t,r])},sm=({children:e,language:n,code:t,theme:r,prism:o})=>{const i=n.toLowerCase(),a=nm(i,r),s=tm(a),l=rm(a),p=o.languages[i],g=am({prism:o,language:i,code:t,grammar:p});return e({tokens:g,className:`prism-code language-${i}`,style:a!=null?a.root:{},getLineProps:s,getTokenProps:l})},lm=e=>z.createElement(sm,Po(Ye({},e),{prism:e.prism||x,theme:e.theme||Rc,code:e.code,language:e.language}));/*! Bundled license information:

prismjs/prism.js:
  (**
   * Prism: Lightweight, robust, elegant syntax highlighting
   *
   * @license MIT <https://opensource.org/licenses/MIT>
   * @author Lea Verou <https://lea.verou.me>
   * @namespace
   * @public
   *)
*/const Tc=z.createContext(void 0),Ac=z.createContext(void 0),Pc=()=>{const e=z.useContext(Tc);if(e===void 0)throw new Error("Could not find nearest <CodeBlock /> component. Please wrap this component with a <CodeBlock /> component.");return e},Wa=()=>{const e=z.useContext(Ac);if(e===void 0)throw new Error("Could not find nearest <CodeBlock.Code /> component. Please wrap this component with <CodeBlock.Code /> component.");return e},um=(e,n)=>n.some(t=>{if(typeof t=="number")return e===t;const[r,o]=t.split(":").map(i=>parseInt(i));return r<=e&&e<=o}),cm=(e,n,t)=>t.some(([r,[o,i]])=>r===e&&o<=n&&n<=i),pm=e=>e.map(n=>{n=n.startsWith("/")?n:"/"+n;const[,t,r="0:Infinity"]=n.split("/"),[o,i=o]=r.split(":").map(a=>Number(a));return[t,[o,i]]}),hn=({code:e,words:n=[],lines:t=[],children:r,...o})=>{const i=z.useMemo(()=>pm(n),[n]);return I.jsx(Tc.Provider,{value:{code:e.trim(),words:i,lines:t,...o},children:r})},dm=({as:e,children:n,...t},r)=>{const{lines:o,words:i,...a}=Pc(),s=e??"pre";return I.jsx(lm,{...a,children:l=>I.jsx(s,{...t,ref:r,children:l.tokens.map((p,g)=>{const y=g+1,_=um(y,o);return I.jsx(Ac.Provider,{value:{highlight:l,line:p,lineNumber:y},children:typeof n=="function"?n({isLineHighlighted:_,lineNumber:y},g):n},g)})})})},fm=({as:e,children:n,className:t,...r},o)=>{const{highlight:i,line:a}=Wa(),{getLineProps:s}=i,l=e??"div";return I.jsx(l,{...s({line:a,className:t}),...r,ref:o,children:n})},mm=({as:e,children:n=({children:i})=>I.jsx("span",{children:i}),className:t,...r},o)=>{const{words:i}=Pc(),{line:a,highlight:s,lineNumber:l}=Wa(),{getTokenProps:p}=s,g=e??"span";return I.jsx(ze.Fragment,{children:a.map((y,_)=>{let{children:w,...f}=p({token:y,className:t}),m=[w];return i.length&&(m=w.split(new RegExp(`(${i.map(([h])=>h).join("|")})`)).filter(Boolean)),I.jsx(ze.Fragment,{children:m.map((h,c)=>I.jsx(g,{...f,...r,ref:o,children:n({children:h,isTokenHighlighted:cm(h,l,i)})},c))},_)})})},ym=({as:e,...n},t)=>{const{lineNumber:r}=Wa(),o=e??"span";return I.jsx(o,{...n,ref:t,children:r})};hn.Code=z.forwardRef(dm);hn.LineContent=z.forwardRef(fm);hn.Token=z.forwardRef(mm);hn.LineNumber=z.forwardRef(ym);var Ic={color:void 0,size:void 0,className:void 0,style:void 0,attr:void 0},ll=ze.createContext&&ze.createContext(Ic),gm=["attr","size","title"];function _m(e,n){if(e==null)return{};var t=hm(e,n),r,o;if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(o=0;o<i.length;o++)r=i[o],!(n.indexOf(r)>=0)&&Object.prototype.propertyIsEnumerable.call(e,r)&&(t[r]=e[r])}return t}function hm(e,n){if(e==null)return{};var t={};for(var r in e)if(Object.prototype.hasOwnProperty.call(e,r)){if(n.indexOf(r)>=0)continue;t[r]=e[r]}return t}function po(){return po=Object.assign?Object.assign.bind():function(e){for(var n=1;n<arguments.length;n++){var t=arguments[n];for(var r in t)Object.prototype.hasOwnProperty.call(t,r)&&(e[r]=t[r])}return e},po.apply(this,arguments)}function ul(e,n){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);n&&(r=r.filter(function(o){return Object.getOwnPropertyDescriptor(e,o).enumerable})),t.push.apply(t,r)}return t}function fo(e){for(var n=1;n<arguments.length;n++){var t=arguments[n]!=null?arguments[n]:{};n%2?ul(Object(t),!0).forEach(function(r){vm(e,r,t[r])}):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):ul(Object(t)).forEach(function(r){Object.defineProperty(e,r,Object.getOwnPropertyDescriptor(t,r))})}return e}function vm(e,n,t){return n=xm(n),n in e?Object.defineProperty(e,n,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[n]=t,e}function xm(e){var n=wm(e,"string");return typeof n=="symbol"?n:n+""}function wm(e,n){if(typeof e!="object"||!e)return e;var t=e[Symbol.toPrimitive];if(t!==void 0){var r=t.call(e,n||"default");if(typeof r!="object")return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return(n==="string"?String:Number)(e)}function Fc(e){return e&&e.map((n,t)=>ze.createElement(n.tag,fo({key:t},n.attr),Fc(n.child)))}function km(e){return n=>ze.createElement(Em,po({attr:fo({},e.attr)},n),Fc(e.child))}function Em(e){var n=t=>{var{attr:r,size:o,title:i}=e,a=_m(e,gm),s=o||t.size||"1em",l;return t.className&&(l=t.className),e.className&&(l=(l?l+" ":"")+e.className),ze.createElement("svg",po({stroke:"currentColor",fill:"currentColor",strokeWidth:"0"},t.attr,r,a,{className:l,style:fo(fo({color:e.color||t.color},t.style),e.style),height:s,width:s,xmlns:"http://www.w3.org/2000/svg"}),i&&ze.createElement("title",null,i),e.children)};return ll!==void 0?ze.createElement(ll.Consumer,null,t=>n(t)):n(Ic)}function Sm(e){return km({tag:"svg",attr:{viewBox:"0 0 24 24"},child:[{tag:"path",attr:{d:"M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"},child:[]}]})(e)}const bm="/_devtools/static/assets/nestipy-BIjLuvV2.png",Cm="Unauthorized",Nm="HttpException",Rm="401 - Unauthorized ",Tm="/home/tsiresy/work/python/nestipy/example",Am={method:"GET",host:"http://127.0.0.1:8000"},Pm=[{filename:"home/tsiresy/work/python/nestipy/src/nestipy/core/router/router_proxy.py",lineno:117,name:"request_handler",code:`import dataclasses
import os
import sys
import traceback
import typing
from typing import Type, Union

from pydantic import BaseModel

from nestipy.common.exception import HttpException
from nestipy.common.exception.http import ExceptionDetail, RequestTrack, Traceback
from nestipy.common.exception.message import HttpStatusMessages
from nestipy.common.exception.status import HttpStatus
from nestipy.common.http_ import Request, Response
from nestipy.common.logger import logger
from nestipy.common.utils import snakecase_to_camelcase
from nestipy.core.exception.processor import ExceptionFilterHandler
from nestipy.core.guards import GuardProcessor
from nestipy.core.interceptor import RequestInterceptor
from nestipy.core.middleware import MiddlewareExecutor
from nestipy.core.template import TemplateRendererProcessor
from nestipy.ioc import NestipyContainer
from nestipy.ioc import RequestContextContainer
from nestipy.types_ import NextFn, CallableHandler
from .route_explorer import RouteExplorer
from ..adapter.http_adapter import HttpAdapter
from ..context.execution_context import ExecutionContext
from ...openapi.openapi_docs.v3 import Operation, PathItem, Response as ApiResponse


class RouterProxy:
    def __init__(self, router: HttpAdapter, ):
        self.router = router
        self._template_processor = TemplateRendererProcessor(router)

    def apply_routes(self, modules: list[Union[Type, object]], prefix: str = ""):
        _prefix: Union[str | None] = f"/{prefix.strip('/')}" if prefix is not None and prefix.strip() != "" else None
        json_paths = {}
        json_schemas = {}
        for module_ref in modules:
            routes = RouteExplorer.explore(module_ref)
            for route in routes:
                path = f"{_prefix.rstrip('/')}/{route['path'].strip('/')}".rstrip('/') if _prefix else route['path']
                methods = route['request_method']
                method_name = route['method_name']
                controller = route['controller']
                handler = self.create_request_handler(module_ref, controller, method_name)
                for method in methods:
                    getattr(self.router, method.lower())(path, handler, route)
                    # OPEN API REGISTER
                    if path in json_paths:
                        route_path = json_paths[path]
                    else:
                        route_path = {}
                    if "responses" not in route['openapi'].keys():
                        route['openapi']["responses"] = {200: ApiResponse()}
                    json_schemas = {**json_schemas, **route['schemas']}
                    if 'no_swagger' not in route['openapi'].keys():
                        route_path[method.lower()] = Operation(
                            **route['openapi'],
                            summary=snakecase_to_camelcase(method_name)
                        )
                        json_paths[path] = route_path
        paths = {}
        for path, op in json_paths.items():
            paths[path] = PathItem(**op)
        return paths, json_schemas

    def create_request_handler(
            self,
            module_ref: Type,
            controller: Union[object, Type],
            method_name: str
    ) -> CallableHandler:

        async def request_handler(req: "Request", res: "Response", next_fn: NextFn):

            context_container = RequestContextContainer.get_instance()
            container = NestipyContainer.get_instance()
            controller_method_handler = getattr(controller, method_name)
            execution_context = ExecutionContext(
                self.router,
                module_ref,
                controller,
                controller_method_handler,
                req,
                res
            )
            # setup container for query params, route params, request, response, session, etc..
            context_container.set_execution_context(execution_context)
            handler_response: Response
            try:
                # TODO : Refactor
                guard_processor: GuardProcessor = await NestipyContainer.get_instance().get(GuardProcessor)
                can_activate = await guard_processor.process(execution_context)
                if not can_activate[0]:
                    # Raise error
                    raise HttpException(
                        HttpStatus.UNAUTHORIZED,
                        HttpStatusMessages.UNAUTHORIZED,
                        details=f"Not authorized from guard {can_activate[1]}"
                    )

                # create next_function that call catch
                async def next_fn_middleware(ex: typing.Any = None):
                    if ex is not None:
                        return await self._ensure_response(res, await next_fn(ex))
                    return await container.get(controller, method_name)

                async def next_fn_interceptor(ex: typing.Any = None):
                    if ex is not None:
                        return await self._ensure_response(res, await next_fn(ex))
                    return await MiddlewareExecutor(req, res, next_fn_middleware).execute()

                #  execute Interceptor by using middleware execution as next_handler
                interceptor: RequestInterceptor = await container.get(RequestInterceptor)
                result = await interceptor.intercept(execution_context, next_fn_interceptor)
                if result is None:
                    raise HttpException(
                        HttpStatus.BAD_REQUEST,
                        "Handler not called because of interceptor: Invalid Request"
                    )
                # process template rendering
                if self._template_processor.can_process(controller_method_handler, result):
                    result = await res.html(self._template_processor.render())
                # transform result to response
                handler_response = await self._ensure_response(res, result)

            except Exception as e:
                tb = traceback.format_exc()
                logger.error(e)
                logger.error(tb)
                if not isinstance(e, HttpException):
                    e = HttpException(HttpStatus.INTERNAL_SERVER_ERROR, str(e), str(tb))
                track = self.get_full_traceback_details(req, e.message, os.getcwd())
                e.track_back = track
                # Call exception catch
                exception_handler = await container.get(ExceptionFilterHandler)
                result = await exception_handler.catch(e, execution_context)
                if result:
                    handler_response = await self._ensure_response(res, result)
                else:
                    handler_response = await self._ensure_response(res, await next_fn(e))
            finally:
                #  reset request context container
                context_container.destroy()
            return handler_response

        return request_handler

    @classmethod
    async def _ensure_response(cls, res: "Response", result: Union["Response", str, dict, list]) -> "Response":

        if isinstance(result, (str, int, float)):
            return await res.send(content=str(result))
        elif isinstance(result, (list, dict)):
            return await res.json(content=result)
        elif dataclasses.is_dataclass(result):
            return await res.json(
                content=dataclasses.asdict(typing.cast(dataclasses.dataclass, result)),
            )
        elif isinstance(result, BaseModel):
            return await res.json(content=result.dict())
        elif isinstance(result, Response):
            return result
        else:
            return await res.json(content={'error': 'Unknown response format'}, status_code=403)

    @classmethod
    def get_code_context(cls, filename, lineno, n):
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
            return ''.join(lines)
        except Exception as e:
            return f"Could not read file {filename}: {str(e)}"

    @classmethod
    def get_full_traceback_details(cls, req: Request, exception: typing.Any, file_path: str):
        exc_type, exc_value, exc_tb = sys.exc_info()
        traceback_details = []

        # Extracting traceback details
        tb = exc_tb
        while tb is not None:
            filename: str = tb.tb_frame.f_code.co_filename
            frame_info = Traceback(
                filename=f"{filename.replace(file_path, '').strip('/')}",
                lineno=tb.tb_lineno,
                name=tb.tb_frame.f_code.co_name,
                code=cls.get_code_context(tb.tb_frame.f_code.co_filename, tb.tb_lineno, 5),
                is_package=filename.startswith(file_path)
            )
            traceback_details.append(frame_info)
            tb = tb.tb_next
        return ExceptionDetail(
            exception=exception,
            type=exc_type.__name__,
            root=file_path,
            traceback=traceback_details,
            request=RequestTrack(method=req.method, host=req.host),
            message=str(exc_value)
        )
`,is_package:!1},{filename:"home/tsiresy/work/python/nestipy/src/nestipy/core/interceptor/processor.py",lineno:47,name:"intercept",code:`from typing import TYPE_CHECKING

from nestipy.common.decorator import Injectable
from nestipy.common.helpers import SpecialProviderExtractor
from nestipy.common.interceptor import NestipyInterceptor, InterceptorKey
from nestipy.core.constant import APP_INTERCEPTOR
from nestipy.core.context.execution_context import ExecutionContext
from nestipy.ioc import NestipyContainer
from nestipy.metadata import ClassMetadata, Reflect

if TYPE_CHECKING:
    from nestipy.types_.handler import NextFn


@Injectable()
class RequestInterceptor(NestipyInterceptor, SpecialProviderExtractor):
    context: ExecutionContext

    def __init__(self):
        self.container = NestipyContainer.get_instance()

    async def intercept(self, context: ExecutionContext, next_fn: "NextFn"):
        self.context = context
        handler_module_class = context.get_module()
        handler_class = context.get_class()
        handler = context.get_handler()

        global_interceptors = context.get_adapter().get_global_interceptors()
        module_interceptors = self.extract_special_providers(
            handler_module_class,
            NestipyInterceptor,
            APP_INTERCEPTOR
        )
        class_interceptors = Reflect.get_metadata(handler_class, InterceptorKey.Meta, [])
        handler_interceptors = Reflect.get_metadata(handler, InterceptorKey.Meta, [])
        all_interceptors = handler_interceptors + class_interceptors + module_interceptors + global_interceptors
        # setup dependency as the same as the container
        for intercept in all_interceptors:
            if issubclass(intercept, NestipyInterceptor):
                # Put dependency
                services = self.container.get_all_services()
                Reflect.set_metadata(
                    intercept, ClassMetadata.Metadata,
                    ClassMetadata(handler_class, global_providers=services)
                )

        return await self._recursive_aplly_interceptor(0, all_interceptors, next_fn)

    async def _recursive_aplly_interceptor(self, index: int, all_interceptors: list, next_fn: "NextFn"):
        if len(all_interceptors) > index:
            interceptor = all_interceptors[index]
            instance: NestipyInterceptor = await self.container.get(interceptor)

            async def _next_fn():
                return await instance.intercept(self.context, next_fn)

            return await self._recursive_aplly_interceptor(index + 1, all_interceptors, _next_fn)
        else:
            return await next_fn()


__all__ = [
    "RequestInterceptor"
]
`,is_package:!1},{filename:"home/tsiresy/work/python/nestipy/src/nestipy/core/interceptor/processor.py",lineno:57,name:"_recursive_aplly_interceptor",code:`from typing import TYPE_CHECKING

from nestipy.common.decorator import Injectable
from nestipy.common.helpers import SpecialProviderExtractor
from nestipy.common.interceptor import NestipyInterceptor, InterceptorKey
from nestipy.core.constant import APP_INTERCEPTOR
from nestipy.core.context.execution_context import ExecutionContext
from nestipy.ioc import NestipyContainer
from nestipy.metadata import ClassMetadata, Reflect

if TYPE_CHECKING:
    from nestipy.types_.handler import NextFn


@Injectable()
class RequestInterceptor(NestipyInterceptor, SpecialProviderExtractor):
    context: ExecutionContext

    def __init__(self):
        self.container = NestipyContainer.get_instance()

    async def intercept(self, context: ExecutionContext, next_fn: "NextFn"):
        self.context = context
        handler_module_class = context.get_module()
        handler_class = context.get_class()
        handler = context.get_handler()

        global_interceptors = context.get_adapter().get_global_interceptors()
        module_interceptors = self.extract_special_providers(
            handler_module_class,
            NestipyInterceptor,
            APP_INTERCEPTOR
        )
        class_interceptors = Reflect.get_metadata(handler_class, InterceptorKey.Meta, [])
        handler_interceptors = Reflect.get_metadata(handler, InterceptorKey.Meta, [])
        all_interceptors = handler_interceptors + class_interceptors + module_interceptors + global_interceptors
        # setup dependency as the same as the container
        for intercept in all_interceptors:
            if issubclass(intercept, NestipyInterceptor):
                # Put dependency
                services = self.container.get_all_services()
                Reflect.set_metadata(
                    intercept, ClassMetadata.Metadata,
                    ClassMetadata(handler_class, global_providers=services)
                )

        return await self._recursive_aplly_interceptor(0, all_interceptors, next_fn)

    async def _recursive_aplly_interceptor(self, index: int, all_interceptors: list, next_fn: "NextFn"):
        if len(all_interceptors) > index:
            interceptor = all_interceptors[index]
            instance: NestipyInterceptor = await self.container.get(interceptor)

            async def _next_fn():
                return await instance.intercept(self.context, next_fn)

            return await self._recursive_aplly_interceptor(index + 1, all_interceptors, _next_fn)
        else:
            return await next_fn()


__all__ = [
    "RequestInterceptor"
]
`,is_package:!1},{filename:"home/tsiresy/work/python/nestipy/src/nestipy/core/interceptor/processor.py",lineno:59,name:"_recursive_aplly_interceptor",code:`from typing import TYPE_CHECKING

from nestipy.common.decorator import Injectable
from nestipy.common.helpers import SpecialProviderExtractor
from nestipy.common.interceptor import NestipyInterceptor, InterceptorKey
from nestipy.core.constant import APP_INTERCEPTOR
from nestipy.core.context.execution_context import ExecutionContext
from nestipy.ioc import NestipyContainer
from nestipy.metadata import ClassMetadata, Reflect

if TYPE_CHECKING:
    from nestipy.types_.handler import NextFn


@Injectable()
class RequestInterceptor(NestipyInterceptor, SpecialProviderExtractor):
    context: ExecutionContext

    def __init__(self):
        self.container = NestipyContainer.get_instance()

    async def intercept(self, context: ExecutionContext, next_fn: "NextFn"):
        self.context = context
        handler_module_class = context.get_module()
        handler_class = context.get_class()
        handler = context.get_handler()

        global_interceptors = context.get_adapter().get_global_interceptors()
        module_interceptors = self.extract_special_providers(
            handler_module_class,
            NestipyInterceptor,
            APP_INTERCEPTOR
        )
        class_interceptors = Reflect.get_metadata(handler_class, InterceptorKey.Meta, [])
        handler_interceptors = Reflect.get_metadata(handler, InterceptorKey.Meta, [])
        all_interceptors = handler_interceptors + class_interceptors + module_interceptors + global_interceptors
        # setup dependency as the same as the container
        for intercept in all_interceptors:
            if issubclass(intercept, NestipyInterceptor):
                # Put dependency
                services = self.container.get_all_services()
                Reflect.set_metadata(
                    intercept, ClassMetadata.Metadata,
                    ClassMetadata(handler_class, global_providers=services)
                )

        return await self._recursive_aplly_interceptor(0, all_interceptors, next_fn)

    async def _recursive_aplly_interceptor(self, index: int, all_interceptors: list, next_fn: "NextFn"):
        if len(all_interceptors) > index:
            interceptor = all_interceptors[index]
            instance: NestipyInterceptor = await self.container.get(interceptor)

            async def _next_fn():
                return await instance.intercept(self.context, next_fn)

            return await self._recursive_aplly_interceptor(index + 1, all_interceptors, _next_fn)
        else:
            return await next_fn()


__all__ = [
    "RequestInterceptor"
]
`,is_package:!1},{filename:"home/tsiresy/work/python/nestipy/src/nestipy/core/interceptor/processor.py",lineno:55,name:"_next_fn",code:`from typing import TYPE_CHECKING

from nestipy.common.decorator import Injectable
from nestipy.common.helpers import SpecialProviderExtractor
from nestipy.common.interceptor import NestipyInterceptor, InterceptorKey
from nestipy.core.constant import APP_INTERCEPTOR
from nestipy.core.context.execution_context import ExecutionContext
from nestipy.ioc import NestipyContainer
from nestipy.metadata import ClassMetadata, Reflect

if TYPE_CHECKING:
    from nestipy.types_.handler import NextFn


@Injectable()
class RequestInterceptor(NestipyInterceptor, SpecialProviderExtractor):
    context: ExecutionContext

    def __init__(self):
        self.container = NestipyContainer.get_instance()

    async def intercept(self, context: ExecutionContext, next_fn: "NextFn"):
        self.context = context
        handler_module_class = context.get_module()
        handler_class = context.get_class()
        handler = context.get_handler()

        global_interceptors = context.get_adapter().get_global_interceptors()
        module_interceptors = self.extract_special_providers(
            handler_module_class,
            NestipyInterceptor,
            APP_INTERCEPTOR
        )
        class_interceptors = Reflect.get_metadata(handler_class, InterceptorKey.Meta, [])
        handler_interceptors = Reflect.get_metadata(handler, InterceptorKey.Meta, [])
        all_interceptors = handler_interceptors + class_interceptors + module_interceptors + global_interceptors
        # setup dependency as the same as the container
        for intercept in all_interceptors:
            if issubclass(intercept, NestipyInterceptor):
                # Put dependency
                services = self.container.get_all_services()
                Reflect.set_metadata(
                    intercept, ClassMetadata.Metadata,
                    ClassMetadata(handler_class, global_providers=services)
                )

        return await self._recursive_aplly_interceptor(0, all_interceptors, next_fn)

    async def _recursive_aplly_interceptor(self, index: int, all_interceptors: list, next_fn: "NextFn"):
        if len(all_interceptors) > index:
            interceptor = all_interceptors[index]
            instance: NestipyInterceptor = await self.container.get(interceptor)

            async def _next_fn():
                return await instance.intercept(self.context, next_fn)

            return await self._recursive_aplly_interceptor(index + 1, all_interceptors, _next_fn)
        else:
            return await next_fn()


__all__ = [
    "RequestInterceptor"
]
`,is_package:!1},{filename:"app_controller.py",lineno:66,name:"intercept",code:`import dataclasses
import os.path
import shutil
from typing import Any, Annotated, Optional, Type

from pydantic import BaseModel

from app_provider import AppProvider
from nestipy.common import Controller, Injectable, Post, Get, logger, UploadFile, HttpStatus, HttpStatusMessages
from nestipy.common import ExceptionFilter, Catch, UseFilters
from nestipy.common import HttpException, apply_decorators
from nestipy.common import NestipyInterceptor, UseInterceptors, Render
from nestipy.common import Request, Response
from nestipy.core import ArgumentHost, ExecutionContext
from nestipy.ioc import Inject, Req, Res, Body, Cookie, Session, Header, create_type_annotated, RequestContextContainer
from nestipy.openapi import ApiResponse, ApiParameter, ApiConsumer
from nestipy.openapi import ApiTags, ApiOkResponse, ApiNotFoundResponse, ApiCreatedResponse, NoSwagger, ApiBody
from nestipy.openapi.openapi_docs.v3 import Parameter, ParameterLocation, Schema
from nestipy.types_ import NextFn


def user_callback(_name: str, _token: Optional[str], _type_ref: Type, _request_context: RequestContextContainer):
    return "User"


User = create_type_annotated(user_callback, "user")


class Test2(BaseModel):
    name2: str


@dataclasses.dataclass
class Test3:
    name3: str


class TestBody(BaseModel):
    image: UploadFile
    test2: Test2
    test3: Test3


class UnauthorizedResponse(BaseModel):
    status: int = 401
    message: str
    details: str


@Catch()
class HttpExceptionFilter(ExceptionFilter):
    async def catch(self, exception: HttpException, host: ArgumentHost) -> Any:
        print('Catcher')


@Catch()
class Http2ExceptionFilter(ExceptionFilter):
    async def catch(self, exception: HttpException, host: ArgumentHost) -> Any:
        print('Catcher2')
        return None


@Injectable()
class TestInterceptor(NestipyInterceptor):
    async def intercept(self, context: ExecutionContext, next_fn: NextFn):
        return await next_fn()


@Injectable()
class TestMethodInterceptor(NestipyInterceptor):
    async def intercept(self, context: ExecutionContext, next_fn: NextFn):
        return await next_fn()


def ApiDecorator():
    return apply_decorators(
        ApiNotFoundResponse(UnauthorizedResponse),
        UseInterceptors(TestInterceptor)
    )


@Controller()
@ApiTags('App')
@ApiDecorator()
@UseFilters(Http2ExceptionFilter)
class AppController:
    provider: Annotated[AppProvider, Inject()]

    @NoSwagger()
    @Render('index.html')
    @Get()
    async def test(
            self,
            req: Annotated[Request, Req()],
            res: Annotated[Response, Res()],
            headers: Annotated[dict, Header()],
            cookies: Annotated[dict, Cookie()],
            user_id: Annotated[str, Session('user_id')],
            sessions: Annotated[dict, Session()]
    ):
        # req.session['user_id'] = 2
        # res.cookie('test', 'test-cookie')
        logger.info(sessions)
        raise HttpException(HttpStatus.UNAUTHORIZED, HttpStatusMessages.UNAUTHORIZED)
        # return {'title': 'Hello'}
        # return await res.render('index.html', {'title': 'Hello'})

    @Post()
    @ApiBody(TestBody, ApiConsumer.MULTIPART)
    @ApiCreatedResponse()
    @ApiResponse(401, UnauthorizedResponse)
    @ApiOkResponse()
    @UseInterceptors(TestMethodInterceptor)
    @ApiParameter(
        Parameter(in_=ParameterLocation.QUERY, name="param", schema=Schema(type="string"))
    )
    @UseFilters(HttpExceptionFilter)
    async def post(
            self,
            res: Annotated[Response, Res()],
            user: Annotated[str, User()],
            body: Annotated[TestBody, Body('latin-1')]
    ):
        print(user)
        file_path = os.path.join(os.path.dirname(__file__), f"nestipy_{body.image.filename}")
        file = open(file_path, "wb")
        shutil.copyfileobj(body.image.file, file)
        file.close()
        return {"uploaded": "Ok"}
        # raise HttpException(HttpStatus.UNAUTHORIZED, HttpStatusMessages.UNAUTHORIZED)
`,is_package:!0},{filename:"home/tsiresy/work/python/nestipy/src/nestipy/core/router/router_proxy.py",lineno:113,name:"next_fn_interceptor",code:`import dataclasses
import os
import sys
import traceback
import typing
from typing import Type, Union

from pydantic import BaseModel

from nestipy.common.exception import HttpException
from nestipy.common.exception.http import ExceptionDetail, RequestTrack, Traceback
from nestipy.common.exception.message import HttpStatusMessages
from nestipy.common.exception.status import HttpStatus
from nestipy.common.http_ import Request, Response
from nestipy.common.logger import logger
from nestipy.common.utils import snakecase_to_camelcase
from nestipy.core.exception.processor import ExceptionFilterHandler
from nestipy.core.guards import GuardProcessor
from nestipy.core.interceptor import RequestInterceptor
from nestipy.core.middleware import MiddlewareExecutor
from nestipy.core.template import TemplateRendererProcessor
from nestipy.ioc import NestipyContainer
from nestipy.ioc import RequestContextContainer
from nestipy.types_ import NextFn, CallableHandler
from .route_explorer import RouteExplorer
from ..adapter.http_adapter import HttpAdapter
from ..context.execution_context import ExecutionContext
from ...openapi.openapi_docs.v3 import Operation, PathItem, Response as ApiResponse


class RouterProxy:
    def __init__(self, router: HttpAdapter, ):
        self.router = router
        self._template_processor = TemplateRendererProcessor(router)

    def apply_routes(self, modules: list[Union[Type, object]], prefix: str = ""):
        _prefix: Union[str | None] = f"/{prefix.strip('/')}" if prefix is not None and prefix.strip() != "" else None
        json_paths = {}
        json_schemas = {}
        for module_ref in modules:
            routes = RouteExplorer.explore(module_ref)
            for route in routes:
                path = f"{_prefix.rstrip('/')}/{route['path'].strip('/')}".rstrip('/') if _prefix else route['path']
                methods = route['request_method']
                method_name = route['method_name']
                controller = route['controller']
                handler = self.create_request_handler(module_ref, controller, method_name)
                for method in methods:
                    getattr(self.router, method.lower())(path, handler, route)
                    # OPEN API REGISTER
                    if path in json_paths:
                        route_path = json_paths[path]
                    else:
                        route_path = {}
                    if "responses" not in route['openapi'].keys():
                        route['openapi']["responses"] = {200: ApiResponse()}
                    json_schemas = {**json_schemas, **route['schemas']}
                    if 'no_swagger' not in route['openapi'].keys():
                        route_path[method.lower()] = Operation(
                            **route['openapi'],
                            summary=snakecase_to_camelcase(method_name)
                        )
                        json_paths[path] = route_path
        paths = {}
        for path, op in json_paths.items():
            paths[path] = PathItem(**op)
        return paths, json_schemas

    def create_request_handler(
            self,
            module_ref: Type,
            controller: Union[object, Type],
            method_name: str
    ) -> CallableHandler:

        async def request_handler(req: "Request", res: "Response", next_fn: NextFn):

            context_container = RequestContextContainer.get_instance()
            container = NestipyContainer.get_instance()
            controller_method_handler = getattr(controller, method_name)
            execution_context = ExecutionContext(
                self.router,
                module_ref,
                controller,
                controller_method_handler,
                req,
                res
            )
            # setup container for query params, route params, request, response, session, etc..
            context_container.set_execution_context(execution_context)
            handler_response: Response
            try:
                # TODO : Refactor
                guard_processor: GuardProcessor = await NestipyContainer.get_instance().get(GuardProcessor)
                can_activate = await guard_processor.process(execution_context)
                if not can_activate[0]:
                    # Raise error
                    raise HttpException(
                        HttpStatus.UNAUTHORIZED,
                        HttpStatusMessages.UNAUTHORIZED,
                        details=f"Not authorized from guard {can_activate[1]}"
                    )

                # create next_function that call catch
                async def next_fn_middleware(ex: typing.Any = None):
                    if ex is not None:
                        return await self._ensure_response(res, await next_fn(ex))
                    return await container.get(controller, method_name)

                async def next_fn_interceptor(ex: typing.Any = None):
                    if ex is not None:
                        return await self._ensure_response(res, await next_fn(ex))
                    return await MiddlewareExecutor(req, res, next_fn_middleware).execute()

                #  execute Interceptor by using middleware execution as next_handler
                interceptor: RequestInterceptor = await container.get(RequestInterceptor)
                result = await interceptor.intercept(execution_context, next_fn_interceptor)
                if result is None:
                    raise HttpException(
                        HttpStatus.BAD_REQUEST,
                        "Handler not called because of interceptor: Invalid Request"
                    )
                # process template rendering
                if self._template_processor.can_process(controller_method_handler, result):
                    result = await res.html(self._template_processor.render())
                # transform result to response
                handler_response = await self._ensure_response(res, result)

            except Exception as e:
                tb = traceback.format_exc()
                logger.error(e)
                logger.error(tb)
                if not isinstance(e, HttpException):
                    e = HttpException(HttpStatus.INTERNAL_SERVER_ERROR, str(e), str(tb))
                track = self.get_full_traceback_details(req, e.message, os.getcwd())
                e.track_back = track
                # Call exception catch
                exception_handler = await container.get(ExceptionFilterHandler)
                result = await exception_handler.catch(e, execution_context)
                if result:
                    handler_response = await self._ensure_response(res, result)
                else:
                    handler_response = await self._ensure_response(res, await next_fn(e))
            finally:
                #  reset request context container
                context_container.destroy()
            return handler_response

        return request_handler

    @classmethod
    async def _ensure_response(cls, res: "Response", result: Union["Response", str, dict, list]) -> "Response":

        if isinstance(result, (str, int, float)):
            return await res.send(content=str(result))
        elif isinstance(result, (list, dict)):
            return await res.json(content=result)
        elif dataclasses.is_dataclass(result):
            return await res.json(
                content=dataclasses.asdict(typing.cast(dataclasses.dataclass, result)),
            )
        elif isinstance(result, BaseModel):
            return await res.json(content=result.dict())
        elif isinstance(result, Response):
            return result
        else:
            return await res.json(content={'error': 'Unknown response format'}, status_code=403)

    @classmethod
    def get_code_context(cls, filename, lineno, n):
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
            return ''.join(lines)
        except Exception as e:
            return f"Could not read file {filename}: {str(e)}"

    @classmethod
    def get_full_traceback_details(cls, req: Request, exception: typing.Any, file_path: str):
        exc_type, exc_value, exc_tb = sys.exc_info()
        traceback_details = []

        # Extracting traceback details
        tb = exc_tb
        while tb is not None:
            filename: str = tb.tb_frame.f_code.co_filename
            frame_info = Traceback(
                filename=f"{filename.replace(file_path, '').strip('/')}",
                lineno=tb.tb_lineno,
                name=tb.tb_frame.f_code.co_name,
                code=cls.get_code_context(tb.tb_frame.f_code.co_filename, tb.tb_lineno, 5),
                is_package=filename.startswith(file_path)
            )
            traceback_details.append(frame_info)
            tb = tb.tb_next
        return ExceptionDetail(
            exception=exception,
            type=exc_type.__name__,
            root=file_path,
            traceback=traceback_details,
            request=RequestTrack(method=req.method, host=req.host),
            message=str(exc_value)
        )
`,is_package:!1},{filename:"home/tsiresy/work/python/nestipy/src/nestipy/core/middleware/executor.py",lineno:56,name:"execute",code:`import inspect
import re
import traceback
from typing import Callable, Any

from nestipy.ioc import MiddlewareContainer, MiddlewareProxy

from nestipy.common.logger import logger
from nestipy.common.http_ import Request, Response
from nestipy.common.middleware import NestipyMiddleware
from nestipy.types_ import HTTPMethod


def uniq_middleware_list(data: list[MiddlewareProxy]) -> list:
    uniq_middleware = []
    uniq_data = []
    for d in data:
        if d.middleware not in uniq_middleware:
            uniq_data.append(d)
            uniq_middleware.append(d.middleware)
    return uniq_data


class MiddlewareExecutor:
    def __init__(self, req: Request, res: Response, next_fn: Callable):
        self.container = MiddlewareContainer.get_instance()
        # load all middleware inside a container
        self._middlewares: list[MiddlewareProxy] = self.container.all()
        self._req = req
        self._res = res
        self._next_fn = next_fn

    async def execute(self):
        middleware_to_apply = []
        for proxy in self._middlewares:
            if (self._is_match(proxy.route.url) and not self._is_exclude
                (proxy.path_excludes,
                 proxy.route.url
                 ) and self._is_method_match(
                proxy.route.method
            )
            ):
                for p in proxy.middlewares:
                    p = MiddlewareProxy.form_dict(
                        p,
                        proxy.route,
                        proxy.path_excludes
                    )
                    self.container.add_singleton(p)
                    middleware_to_apply.append(p)
        # get all middleware that match request path
        if len(middleware_to_apply) == 0:
            # if no middleware call next_fn that call handler
            return await self._next_fn()
        middleware_to_apply = uniq_middleware_list(middleware_to_apply)
        return await self._recursively_call_middleware(0, middleware_to_apply)

    async def _create_middleware_callable(self, proxy: MiddlewareProxy):
        if inspect.isclass(proxy.middleware) and issubclass(proxy.middleware, NestipyMiddleware):
            try:
                #  get instance of Middleware
                instance = await self.container.get(proxy)
                # get use method if it is a middleware class
                return getattr(instance, 'use')
            except Exception as e:
                tb = traceback.format_exc()
                logger.error(e)
                logger.error(tb)
                return None
        elif inspect.isfunction(proxy.middleware):
            return proxy.middleware
        else:
            raise Exception('Middleware must be a function or a class that extends NestipyMiddleware')

    async def _recursively_call_middleware(self, index: int, middlewares: list[MiddlewareProxy]) -> Any:
        current = middlewares[index]
        to_call = await self._create_middleware_callable(current)
        if index != len(middlewares) - 1:
            # create next_fn that cal next middleware
            async def next_fn():
                return await self._recursively_call_middleware(index + 1, middlewares)

            return await to_call(self._req, self._res, next_fn)
        else:
            return await to_call(self._req, self._res, self._next_fn)

    def _is_match(self, to_match: str, route: str = None) -> bool:
        pattern = re.compile(f"^{to_match}")
        mitch = pattern.match(route or self._req.path, )
        return mitch is not None

    def _is_method_match(self, method: list[HTTPMethod]) -> bool:
        if 'ALL' in method or 'ANY' in method:
            return True
        else:
            return self._req.method.upper() in [m.upper() for m in method]

    def _is_exclude(self, excludes: list[str], to_match: str) -> bool:
        for ex in excludes:
            if self._is_match(to_match, ex):
                return True
        return False
`,is_package:!1},{filename:"home/tsiresy/work/python/nestipy/src/nestipy/core/middleware/executor.py",lineno:83,name:"_recursively_call_middleware",code:`import inspect
import re
import traceback
from typing import Callable, Any

from nestipy.ioc import MiddlewareContainer, MiddlewareProxy

from nestipy.common.logger import logger
from nestipy.common.http_ import Request, Response
from nestipy.common.middleware import NestipyMiddleware
from nestipy.types_ import HTTPMethod


def uniq_middleware_list(data: list[MiddlewareProxy]) -> list:
    uniq_middleware = []
    uniq_data = []
    for d in data:
        if d.middleware not in uniq_middleware:
            uniq_data.append(d)
            uniq_middleware.append(d.middleware)
    return uniq_data


class MiddlewareExecutor:
    def __init__(self, req: Request, res: Response, next_fn: Callable):
        self.container = MiddlewareContainer.get_instance()
        # load all middleware inside a container
        self._middlewares: list[MiddlewareProxy] = self.container.all()
        self._req = req
        self._res = res
        self._next_fn = next_fn

    async def execute(self):
        middleware_to_apply = []
        for proxy in self._middlewares:
            if (self._is_match(proxy.route.url) and not self._is_exclude
                (proxy.path_excludes,
                 proxy.route.url
                 ) and self._is_method_match(
                proxy.route.method
            )
            ):
                for p in proxy.middlewares:
                    p = MiddlewareProxy.form_dict(
                        p,
                        proxy.route,
                        proxy.path_excludes
                    )
                    self.container.add_singleton(p)
                    middleware_to_apply.append(p)
        # get all middleware that match request path
        if len(middleware_to_apply) == 0:
            # if no middleware call next_fn that call handler
            return await self._next_fn()
        middleware_to_apply = uniq_middleware_list(middleware_to_apply)
        return await self._recursively_call_middleware(0, middleware_to_apply)

    async def _create_middleware_callable(self, proxy: MiddlewareProxy):
        if inspect.isclass(proxy.middleware) and issubclass(proxy.middleware, NestipyMiddleware):
            try:
                #  get instance of Middleware
                instance = await self.container.get(proxy)
                # get use method if it is a middleware class
                return getattr(instance, 'use')
            except Exception as e:
                tb = traceback.format_exc()
                logger.error(e)
                logger.error(tb)
                return None
        elif inspect.isfunction(proxy.middleware):
            return proxy.middleware
        else:
            raise Exception('Middleware must be a function or a class that extends NestipyMiddleware')

    async def _recursively_call_middleware(self, index: int, middlewares: list[MiddlewareProxy]) -> Any:
        current = middlewares[index]
        to_call = await self._create_middleware_callable(current)
        if index != len(middlewares) - 1:
            # create next_fn that cal next middleware
            async def next_fn():
                return await self._recursively_call_middleware(index + 1, middlewares)

            return await to_call(self._req, self._res, next_fn)
        else:
            return await to_call(self._req, self._res, self._next_fn)

    def _is_match(self, to_match: str, route: str = None) -> bool:
        pattern = re.compile(f"^{to_match}")
        mitch = pattern.match(route or self._req.path, )
        return mitch is not None

    def _is_method_match(self, method: list[HTTPMethod]) -> bool:
        if 'ALL' in method or 'ANY' in method:
            return True
        else:
            return self._req.method.upper() in [m.upper() for m in method]

    def _is_exclude(self, excludes: list[str], to_match: str) -> bool:
        for ex in excludes:
            if self._is_match(to_match, ex):
                return True
        return False
`,is_package:!1},{filename:"home/tsiresy/work/python/nestipy/src/nestipy/common/middleware/session.py",lineno:48,name:"use",code:`import dataclasses
from base64 import b64decode, b64encode
from typing import Type, Union, Literal

import itsdangerous
import ujson
from itsdangerous.exc import BadSignature

from nestipy.common.decorator import Injectable
from nestipy.common.http_ import Request, Response
from nestipy.common.middleware.interface import NestipyMiddleware
from nestipy.types_ import NextFn


@dataclasses.dataclass
class SessionOption:
    secret_key: str = ''
    session_cookie: str = "session"
    max_age: Union[int, None] = 14 * 24 * 60 * 60
    path: str = "/"
    same_site: Literal["lax", "strict", "none"] = "lax"
    https_only: bool = False
    domain: Union[str, None] = None


def session(option: SessionOption = SessionOption()) -> Type:
    @Injectable()
    class SessionMiddleware(NestipyMiddleware):

        async def use(self, req: Request, res: Response, next_fn: NextFn):
            initial_session_was_empty = True
            signer = itsdangerous.TimestampSigner(str(option.secret_key))
            security_flags = "httponly; samesite=" + option.same_site
            if option.https_only:
                security_flags += "; secure"
            if option.domain is not None:
                security_flags += f"; domain={option.domain}"
            if option.session_cookie in req.cookies:
                data = req.cookies[option.session_cookie].encode("utf-8")
                try:
                    un_sign_data = signer.unsign(data, max_age=option.max_age)
                    req.session = ujson.loads(b64decode(un_sign_data))
                    initial_session_was_empty = False
                except BadSignature:
                    req.session = {}
            else:
                req.session = {}
            result = await next_fn()
            cookie_max_age = f"Max-Age={option.max_age}; " if option.max_age else ""
            header_value = ", ".join([
                f"{key}={value}; path={option.path}; {cookie_max_age}{security_flags}"
                for (key, value) in res.cookies()
            ])
            if header_value:
                header_value += ", "
            if req.session:
                data = b64encode(ujson.dumps(req.session).encode("utf-8"))
                sign_data = signer.sign(data)
                header_value += "{session_cookie}={data}; path={path}; {max_age}{security_flags}".format(  # noqa E501
                    session_cookie=option.session_cookie,
                    data=sign_data.decode("utf-8"),
                    path=option.path,
                    max_age=f"Max-Age={option.max_age}; " if option.max_age else "",
                    security_flags=security_flags,
                )
                res.header('Set-Cookie', header_value)
            elif initial_session_was_empty:
                header_value += "{session_cookie}={data}; path={path}; {expires}{security_flags}".format(  # noqa E501
                    session_cookie=option.session_cookie,
                    data="null",
                    path=option.path,
                    expires="expires=Thu, 01 Jan 1970 00:00:00 GMT; ",
                    security_flags=security_flags,
                )
                res.header("Set-Cookie", header_value)

            return result

    return SessionMiddleware
`,is_package:!1},{filename:"home/tsiresy/work/python/nestipy/src/nestipy/core/middleware/executor.py",lineno:81,name:"next_fn",code:`import inspect
import re
import traceback
from typing import Callable, Any

from nestipy.ioc import MiddlewareContainer, MiddlewareProxy

from nestipy.common.logger import logger
from nestipy.common.http_ import Request, Response
from nestipy.common.middleware import NestipyMiddleware
from nestipy.types_ import HTTPMethod


def uniq_middleware_list(data: list[MiddlewareProxy]) -> list:
    uniq_middleware = []
    uniq_data = []
    for d in data:
        if d.middleware not in uniq_middleware:
            uniq_data.append(d)
            uniq_middleware.append(d.middleware)
    return uniq_data


class MiddlewareExecutor:
    def __init__(self, req: Request, res: Response, next_fn: Callable):
        self.container = MiddlewareContainer.get_instance()
        # load all middleware inside a container
        self._middlewares: list[MiddlewareProxy] = self.container.all()
        self._req = req
        self._res = res
        self._next_fn = next_fn

    async def execute(self):
        middleware_to_apply = []
        for proxy in self._middlewares:
            if (self._is_match(proxy.route.url) and not self._is_exclude
                (proxy.path_excludes,
                 proxy.route.url
                 ) and self._is_method_match(
                proxy.route.method
            )
            ):
                for p in proxy.middlewares:
                    p = MiddlewareProxy.form_dict(
                        p,
                        proxy.route,
                        proxy.path_excludes
                    )
                    self.container.add_singleton(p)
                    middleware_to_apply.append(p)
        # get all middleware that match request path
        if len(middleware_to_apply) == 0:
            # if no middleware call next_fn that call handler
            return await self._next_fn()
        middleware_to_apply = uniq_middleware_list(middleware_to_apply)
        return await self._recursively_call_middleware(0, middleware_to_apply)

    async def _create_middleware_callable(self, proxy: MiddlewareProxy):
        if inspect.isclass(proxy.middleware) and issubclass(proxy.middleware, NestipyMiddleware):
            try:
                #  get instance of Middleware
                instance = await self.container.get(proxy)
                # get use method if it is a middleware class
                return getattr(instance, 'use')
            except Exception as e:
                tb = traceback.format_exc()
                logger.error(e)
                logger.error(tb)
                return None
        elif inspect.isfunction(proxy.middleware):
            return proxy.middleware
        else:
            raise Exception('Middleware must be a function or a class that extends NestipyMiddleware')

    async def _recursively_call_middleware(self, index: int, middlewares: list[MiddlewareProxy]) -> Any:
        current = middlewares[index]
        to_call = await self._create_middleware_callable(current)
        if index != len(middlewares) - 1:
            # create next_fn that cal next middleware
            async def next_fn():
                return await self._recursively_call_middleware(index + 1, middlewares)

            return await to_call(self._req, self._res, next_fn)
        else:
            return await to_call(self._req, self._res, self._next_fn)

    def _is_match(self, to_match: str, route: str = None) -> bool:
        pattern = re.compile(f"^{to_match}")
        mitch = pattern.match(route or self._req.path, )
        return mitch is not None

    def _is_method_match(self, method: list[HTTPMethod]) -> bool:
        if 'ALL' in method or 'ANY' in method:
            return True
        else:
            return self._req.method.upper() in [m.upper() for m in method]

    def _is_exclude(self, excludes: list[str], to_match: str) -> bool:
        for ex in excludes:
            if self._is_match(to_match, ex):
                return True
        return False
`,is_package:!1},{filename:"home/tsiresy/work/python/nestipy/src/nestipy/core/middleware/executor.py",lineno:85,name:"_recursively_call_middleware",code:`import inspect
import re
import traceback
from typing import Callable, Any

from nestipy.ioc import MiddlewareContainer, MiddlewareProxy

from nestipy.common.logger import logger
from nestipy.common.http_ import Request, Response
from nestipy.common.middleware import NestipyMiddleware
from nestipy.types_ import HTTPMethod


def uniq_middleware_list(data: list[MiddlewareProxy]) -> list:
    uniq_middleware = []
    uniq_data = []
    for d in data:
        if d.middleware not in uniq_middleware:
            uniq_data.append(d)
            uniq_middleware.append(d.middleware)
    return uniq_data


class MiddlewareExecutor:
    def __init__(self, req: Request, res: Response, next_fn: Callable):
        self.container = MiddlewareContainer.get_instance()
        # load all middleware inside a container
        self._middlewares: list[MiddlewareProxy] = self.container.all()
        self._req = req
        self._res = res
        self._next_fn = next_fn

    async def execute(self):
        middleware_to_apply = []
        for proxy in self._middlewares:
            if (self._is_match(proxy.route.url) and not self._is_exclude
                (proxy.path_excludes,
                 proxy.route.url
                 ) and self._is_method_match(
                proxy.route.method
            )
            ):
                for p in proxy.middlewares:
                    p = MiddlewareProxy.form_dict(
                        p,
                        proxy.route,
                        proxy.path_excludes
                    )
                    self.container.add_singleton(p)
                    middleware_to_apply.append(p)
        # get all middleware that match request path
        if len(middleware_to_apply) == 0:
            # if no middleware call next_fn that call handler
            return await self._next_fn()
        middleware_to_apply = uniq_middleware_list(middleware_to_apply)
        return await self._recursively_call_middleware(0, middleware_to_apply)

    async def _create_middleware_callable(self, proxy: MiddlewareProxy):
        if inspect.isclass(proxy.middleware) and issubclass(proxy.middleware, NestipyMiddleware):
            try:
                #  get instance of Middleware
                instance = await self.container.get(proxy)
                # get use method if it is a middleware class
                return getattr(instance, 'use')
            except Exception as e:
                tb = traceback.format_exc()
                logger.error(e)
                logger.error(tb)
                return None
        elif inspect.isfunction(proxy.middleware):
            return proxy.middleware
        else:
            raise Exception('Middleware must be a function or a class that extends NestipyMiddleware')

    async def _recursively_call_middleware(self, index: int, middlewares: list[MiddlewareProxy]) -> Any:
        current = middlewares[index]
        to_call = await self._create_middleware_callable(current)
        if index != len(middlewares) - 1:
            # create next_fn that cal next middleware
            async def next_fn():
                return await self._recursively_call_middleware(index + 1, middlewares)

            return await to_call(self._req, self._res, next_fn)
        else:
            return await to_call(self._req, self._res, self._next_fn)

    def _is_match(self, to_match: str, route: str = None) -> bool:
        pattern = re.compile(f"^{to_match}")
        mitch = pattern.match(route or self._req.path, )
        return mitch is not None

    def _is_method_match(self, method: list[HTTPMethod]) -> bool:
        if 'ALL' in method or 'ANY' in method:
            return True
        else:
            return self._req.method.upper() in [m.upper() for m in method]

    def _is_exclude(self, excludes: list[str], to_match: str) -> bool:
        for ex in excludes:
            if self._is_match(to_match, ex):
                return True
        return False
`,is_package:!1},{filename:"home/tsiresy/work/python/nestipy/src/nestipy/common/middleware/session.py",lineno:48,name:"use",code:`import dataclasses
from base64 import b64decode, b64encode
from typing import Type, Union, Literal

import itsdangerous
import ujson
from itsdangerous.exc import BadSignature

from nestipy.common.decorator import Injectable
from nestipy.common.http_ import Request, Response
from nestipy.common.middleware.interface import NestipyMiddleware
from nestipy.types_ import NextFn


@dataclasses.dataclass
class SessionOption:
    secret_key: str = ''
    session_cookie: str = "session"
    max_age: Union[int, None] = 14 * 24 * 60 * 60
    path: str = "/"
    same_site: Literal["lax", "strict", "none"] = "lax"
    https_only: bool = False
    domain: Union[str, None] = None


def session(option: SessionOption = SessionOption()) -> Type:
    @Injectable()
    class SessionMiddleware(NestipyMiddleware):

        async def use(self, req: Request, res: Response, next_fn: NextFn):
            initial_session_was_empty = True
            signer = itsdangerous.TimestampSigner(str(option.secret_key))
            security_flags = "httponly; samesite=" + option.same_site
            if option.https_only:
                security_flags += "; secure"
            if option.domain is not None:
                security_flags += f"; domain={option.domain}"
            if option.session_cookie in req.cookies:
                data = req.cookies[option.session_cookie].encode("utf-8")
                try:
                    un_sign_data = signer.unsign(data, max_age=option.max_age)
                    req.session = ujson.loads(b64decode(un_sign_data))
                    initial_session_was_empty = False
                except BadSignature:
                    req.session = {}
            else:
                req.session = {}
            result = await next_fn()
            cookie_max_age = f"Max-Age={option.max_age}; " if option.max_age else ""
            header_value = ", ".join([
                f"{key}={value}; path={option.path}; {cookie_max_age}{security_flags}"
                for (key, value) in res.cookies()
            ])
            if header_value:
                header_value += ", "
            if req.session:
                data = b64encode(ujson.dumps(req.session).encode("utf-8"))
                sign_data = signer.sign(data)
                header_value += "{session_cookie}={data}; path={path}; {max_age}{security_flags}".format(  # noqa E501
                    session_cookie=option.session_cookie,
                    data=sign_data.decode("utf-8"),
                    path=option.path,
                    max_age=f"Max-Age={option.max_age}; " if option.max_age else "",
                    security_flags=security_flags,
                )
                res.header('Set-Cookie', header_value)
            elif initial_session_was_empty:
                header_value += "{session_cookie}={data}; path={path}; {expires}{security_flags}".format(  # noqa E501
                    session_cookie=option.session_cookie,
                    data="null",
                    path=option.path,
                    expires="expires=Thu, 01 Jan 1970 00:00:00 GMT; ",
                    security_flags=security_flags,
                )
                res.header("Set-Cookie", header_value)

            return result

    return SessionMiddleware
`,is_package:!1},{filename:"home/tsiresy/work/python/nestipy/src/nestipy/core/router/router_proxy.py",lineno:108,name:"next_fn_middleware",code:`import dataclasses
import os
import sys
import traceback
import typing
from typing import Type, Union

from pydantic import BaseModel

from nestipy.common.exception import HttpException
from nestipy.common.exception.http import ExceptionDetail, RequestTrack, Traceback
from nestipy.common.exception.message import HttpStatusMessages
from nestipy.common.exception.status import HttpStatus
from nestipy.common.http_ import Request, Response
from nestipy.common.logger import logger
from nestipy.common.utils import snakecase_to_camelcase
from nestipy.core.exception.processor import ExceptionFilterHandler
from nestipy.core.guards import GuardProcessor
from nestipy.core.interceptor import RequestInterceptor
from nestipy.core.middleware import MiddlewareExecutor
from nestipy.core.template import TemplateRendererProcessor
from nestipy.ioc import NestipyContainer
from nestipy.ioc import RequestContextContainer
from nestipy.types_ import NextFn, CallableHandler
from .route_explorer import RouteExplorer
from ..adapter.http_adapter import HttpAdapter
from ..context.execution_context import ExecutionContext
from ...openapi.openapi_docs.v3 import Operation, PathItem, Response as ApiResponse


class RouterProxy:
    def __init__(self, router: HttpAdapter, ):
        self.router = router
        self._template_processor = TemplateRendererProcessor(router)

    def apply_routes(self, modules: list[Union[Type, object]], prefix: str = ""):
        _prefix: Union[str | None] = f"/{prefix.strip('/')}" if prefix is not None and prefix.strip() != "" else None
        json_paths = {}
        json_schemas = {}
        for module_ref in modules:
            routes = RouteExplorer.explore(module_ref)
            for route in routes:
                path = f"{_prefix.rstrip('/')}/{route['path'].strip('/')}".rstrip('/') if _prefix else route['path']
                methods = route['request_method']
                method_name = route['method_name']
                controller = route['controller']
                handler = self.create_request_handler(module_ref, controller, method_name)
                for method in methods:
                    getattr(self.router, method.lower())(path, handler, route)
                    # OPEN API REGISTER
                    if path in json_paths:
                        route_path = json_paths[path]
                    else:
                        route_path = {}
                    if "responses" not in route['openapi'].keys():
                        route['openapi']["responses"] = {200: ApiResponse()}
                    json_schemas = {**json_schemas, **route['schemas']}
                    if 'no_swagger' not in route['openapi'].keys():
                        route_path[method.lower()] = Operation(
                            **route['openapi'],
                            summary=snakecase_to_camelcase(method_name)
                        )
                        json_paths[path] = route_path
        paths = {}
        for path, op in json_paths.items():
            paths[path] = PathItem(**op)
        return paths, json_schemas

    def create_request_handler(
            self,
            module_ref: Type,
            controller: Union[object, Type],
            method_name: str
    ) -> CallableHandler:

        async def request_handler(req: "Request", res: "Response", next_fn: NextFn):

            context_container = RequestContextContainer.get_instance()
            container = NestipyContainer.get_instance()
            controller_method_handler = getattr(controller, method_name)
            execution_context = ExecutionContext(
                self.router,
                module_ref,
                controller,
                controller_method_handler,
                req,
                res
            )
            # setup container for query params, route params, request, response, session, etc..
            context_container.set_execution_context(execution_context)
            handler_response: Response
            try:
                # TODO : Refactor
                guard_processor: GuardProcessor = await NestipyContainer.get_instance().get(GuardProcessor)
                can_activate = await guard_processor.process(execution_context)
                if not can_activate[0]:
                    # Raise error
                    raise HttpException(
                        HttpStatus.UNAUTHORIZED,
                        HttpStatusMessages.UNAUTHORIZED,
                        details=f"Not authorized from guard {can_activate[1]}"
                    )

                # create next_function that call catch
                async def next_fn_middleware(ex: typing.Any = None):
                    if ex is not None:
                        return await self._ensure_response(res, await next_fn(ex))
                    return await container.get(controller, method_name)

                async def next_fn_interceptor(ex: typing.Any = None):
                    if ex is not None:
                        return await self._ensure_response(res, await next_fn(ex))
                    return await MiddlewareExecutor(req, res, next_fn_middleware).execute()

                #  execute Interceptor by using middleware execution as next_handler
                interceptor: RequestInterceptor = await container.get(RequestInterceptor)
                result = await interceptor.intercept(execution_context, next_fn_interceptor)
                if result is None:
                    raise HttpException(
                        HttpStatus.BAD_REQUEST,
                        "Handler not called because of interceptor: Invalid Request"
                    )
                # process template rendering
                if self._template_processor.can_process(controller_method_handler, result):
                    result = await res.html(self._template_processor.render())
                # transform result to response
                handler_response = await self._ensure_response(res, result)

            except Exception as e:
                tb = traceback.format_exc()
                logger.error(e)
                logger.error(tb)
                if not isinstance(e, HttpException):
                    e = HttpException(HttpStatus.INTERNAL_SERVER_ERROR, str(e), str(tb))
                track = self.get_full_traceback_details(req, e.message, os.getcwd())
                e.track_back = track
                # Call exception catch
                exception_handler = await container.get(ExceptionFilterHandler)
                result = await exception_handler.catch(e, execution_context)
                if result:
                    handler_response = await self._ensure_response(res, result)
                else:
                    handler_response = await self._ensure_response(res, await next_fn(e))
            finally:
                #  reset request context container
                context_container.destroy()
            return handler_response

        return request_handler

    @classmethod
    async def _ensure_response(cls, res: "Response", result: Union["Response", str, dict, list]) -> "Response":

        if isinstance(result, (str, int, float)):
            return await res.send(content=str(result))
        elif isinstance(result, (list, dict)):
            return await res.json(content=result)
        elif dataclasses.is_dataclass(result):
            return await res.json(
                content=dataclasses.asdict(typing.cast(dataclasses.dataclass, result)),
            )
        elif isinstance(result, BaseModel):
            return await res.json(content=result.dict())
        elif isinstance(result, Response):
            return result
        else:
            return await res.json(content={'error': 'Unknown response format'}, status_code=403)

    @classmethod
    def get_code_context(cls, filename, lineno, n):
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
            return ''.join(lines)
        except Exception as e:
            return f"Could not read file {filename}: {str(e)}"

    @classmethod
    def get_full_traceback_details(cls, req: Request, exception: typing.Any, file_path: str):
        exc_type, exc_value, exc_tb = sys.exc_info()
        traceback_details = []

        # Extracting traceback details
        tb = exc_tb
        while tb is not None:
            filename: str = tb.tb_frame.f_code.co_filename
            frame_info = Traceback(
                filename=f"{filename.replace(file_path, '').strip('/')}",
                lineno=tb.tb_lineno,
                name=tb.tb_frame.f_code.co_name,
                code=cls.get_code_context(tb.tb_frame.f_code.co_filename, tb.tb_lineno, 5),
                is_package=filename.startswith(file_path)
            )
            traceback_details.append(frame_info)
            tb = tb.tb_next
        return ExceptionDetail(
            exception=exception,
            type=exc_type.__name__,
            root=file_path,
            traceback=traceback_details,
            request=RequestTrack(method=req.method, host=req.host),
            message=str(exc_value)
        )
`,is_package:!1},{filename:"home/tsiresy/work/python/nestipy/src/nestipy/ioc/container.py",lineno:238,name:"get",code:`import inspect
from functools import lru_cache
from typing import Type, Union, Any, Optional, Callable, Awaitable, TYPE_CHECKING

from nestipy.metadata import ClassMetadata, CtxDepKey, ModuleMetadata, ProviderToken, Reflect
from .context_container import RequestContextContainer
from .dependency import TypeAnnotated
from .meta import ContainerHelper
from .utils import uniq

if TYPE_CHECKING:
    from .provider import ModuleProviderDict

_INIT = "__init__"


class NestipyContainer:
    _instance: "NestipyContainer" = None
    _services = {}
    _global_service_instances = {}
    _singleton_instances = {}
    _singleton_classes = set()
    helper = ContainerHelper()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(NestipyContainer, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def get_instance(cls, *args, **kwargs):
        return NestipyContainer(*args, **kwargs)

    def add_transient(self, service: Type):
        self._services[service] = service

    def add_singleton(self, service: Type):
        self._services[service] = service
        self._singleton_classes.add(service)

    def get_all_services(self) -> list:
        return list(self._services.keys())

    def add_singleton_instance(self, service: Union[Type, str], service_instance: object):
        self._singleton_instances[service] = service_instance

    def get_all_singleton_instance(self) -> list:
        return [v for k, v in self._singleton_instances.items()]

    @classmethod
    @lru_cache()
    def get_global_providers(cls) -> list:
        global_providers = []
        for service in cls._services:
            if service in global_providers:
                continue
            metadata: ClassMetadata = Reflect.get_metadata(service, ClassMetadata.Metadata, None)
            if metadata is not None:
                is_global = Reflect.get_metadata(metadata.get_module(), ModuleMetadata.Global, False)
                is_root = Reflect.get_metadata(metadata.get_module(), ModuleMetadata.Root, False)
                if is_global or is_root:
                    global_providers += Reflect.get_metadata(metadata.get_module(), ModuleMetadata.Providers, [])
        return uniq(global_providers)

    @classmethod
    def get_dependency_metadata(cls, service: Union[Type, object]) -> list:
        from .provider import ModuleProviderDict
        # extract global data from _service, not from module because all provider is already saved in _services of
        # container
        metadata: ClassMetadata = Reflect.get_metadata(service, ClassMetadata.Metadata, None)
        if metadata is not None:
            global_providers = cls.get_global_providers()
            providers, import_providers = metadata.get_service_providers()
            uniq_providers = []
            for m in uniq(providers + global_providers + import_providers):
                if isinstance(m, ModuleProviderDict):
                    uniq_providers.append(m.token)
                else:
                    uniq_providers.append(m)
            return uniq(uniq_providers)
        # raise ValueError(f"Dependency Metadata not found  for {service.__name__} service ")
        return []

    @classmethod
    async def _resolve_context_service(cls, name: str, dep_key: TypeAnnotated, annotation: Union[Type, Any]):
        context_container = RequestContextContainer.get_instance()
        callback = dep_key.metadata.callback
        if inspect.iscoroutinefunction(callback):
            return await callback(name, dep_key.metadata.token, annotation, context_container)
        else:
            return callback(name, dep_key.metadata.token, annotation, context_container)

    async def _resolve_module_provider_dict(self, instance: "ModuleProviderDict", search_scope: list):
        if instance.value:
            return instance.value
        elif instance.existing:
            if isinstance(instance.existing, ProviderToken):
                return await self.get(instance.existing.key)
            else:
                return await self.get(instance.existing)
        elif instance.use_class:
            return await self.get(instance.use_class)
        elif instance.factory:
            return await self.resolve_factory(
                factory=instance.factory,
                inject=instance.inject,
                search_scope=search_scope
            )

        else:
            return None

    async def _check_exist_singleton(self, key: Union[Type, str]):
        from .provider import ModuleProviderDict
        if key in self._singleton_instances:
            instance = self._singleton_instances[key]
            # to keep improve
            if isinstance(instance, ModuleProviderDict):
                search_scope = self.get_dependency_metadata(instance)
                if instance.token in search_scope:
                    value = await self._resolve_module_provider_dict(instance, search_scope=search_scope)
                    # update singleton instance to have the async value from ModuleProviderDict
                    self._singleton_instances[key] = value
                    return value
                else:
                    raise ValueError(
                        f"Service {instance.__class__.__name__} "
                        f"not found in scope")
            else:
                return instance
        return None

    def _check_service(self, key: Union[Type, str], origin: Optional[list] = None) -> tuple:
        if key not in self._services:
            raise ValueError(f"Service {key} not found")
        service = self._services[key]
        if service in (origin or []):
            raise ValueError(f"Circular dependency found  for {service.__name__} service ")
        return service, origin or set()

    async def _resolve_property(
            self,
            key: Union[Type, str],
            origin: Optional[list] = None,
            disable_scope: bool = False
    ):
        service, origin = self._check_service(key, origin)
        search_scope = self.get_dependency_metadata(service)
        origin.add(service)
        annotations: dict = getattr(service, '__annotations__', {})
        for name, param_annotation in annotations.items():
            annotation, dep_key = self.helper.get_type_from_annotation(param_annotation)
            if dep_key.metadata.key is not CtxDepKey.Service:
                dependency = await self._resolve_context_service(name, dep_key, annotation)
                setattr(service, name, dependency)
            elif dep_key.metadata.token in search_scope or annotation in search_scope or disable_scope:
                dependency = await self.get(dep_key.metadata.token or annotation)
                setattr(service, name, dependency)
            else:
                _name: str = annotation.__name__ if not isinstance(annotation, str) else annotation
                raise ValueError(f"Service {_name} not found in scope {search_scope}")
        origin.remove(service)
        self._services[key] = service

    async def _get_method_dependency(self, method_to_resolve: Callable, search_scope: list,
                                     disable_scope: bool = False):
        params = inspect.signature(method_to_resolve).parameters
        args = {}
        for name, param in params.items():
            if name != 'self' and param.annotation is not inspect.Parameter.empty:
                annotation, dep_key = self.helper.get_type_from_annotation(param.annotation)
                if dep_key.metadata.key is not CtxDepKey.Service:
                    dependency = await self._resolve_context_service(name, dep_key, annotation)
                    args[name] = dependency
                elif dep_key.metadata.token in search_scope or annotation in search_scope or disable_scope:
                    dependency = await self.get(dep_key.metadata.token or annotation)
                    args[name] = dependency
                else:
                    _name: str = annotation.__name__ if not isinstance(annotation, str) else annotation
                    raise ValueError(f"Service {_name} not found in scope {search_scope}")
        return args

    @classmethod
    async def _call_method(cls, method: Callable, args: dict):
        if inspect.iscoroutinefunction(method):
            return await method(**args)
        return method(**args)

    async def resolve_factory(self, factory: Callable, inject: list, search_scope: list, disable_scope: bool = False):
        search_scope_by_inject = [m for m in inject if m in search_scope]
        args = await self._get_method_dependency(
            method_to_resolve=factory,
            search_scope=search_scope_by_inject,
            disable_scope=disable_scope
        )
        return await self._call_method(method=factory, args=args)

    async def _resolve_method(
            self,
            key: Union[Type, str, object],
            method: str = _INIT,
            origin: Optional[list] = None,
            disable_scope: bool = False
    ):
        service, origin = self._check_service(key, origin)
        search_scope = self.get_dependency_metadata(service)
        origin.add(service)
        method_to_resolve = getattr(service, method, None)
        if not method_to_resolve:
            raise Exception(f"Method {method} not found in {service.__name__} service ")
        args = await self._get_method_dependency(method_to_resolve, search_scope, disable_scope=disable_scope)
        if method == _INIT:
            result = service(**args)
            if service in self._singleton_classes:
                self._singleton_instances[service] = result
        else:
            # Service must be an instance (controller)
            instance = await self.get(key)
            instance_method = getattr(instance, method, method_to_resolve)
            result = await self._call_method(instance_method, args)

        origin.remove(service)
        return result

    async def get(
            self,
            key: Union[Type, str],
            method: str = _INIT,
            origin: Optional[list] = None,
            disable_scope: Optional[bool] = False
    ) -> Awaitable[object]:
        in_singleton = await self._check_exist_singleton(key=key)
        if in_singleton:
            if method == _INIT:
                return in_singleton
        else:
            await self._resolve_property(key, origin=origin, disable_scope=disable_scope)
        return await self._resolve_method(key, method=method, origin=origin, disable_scope=disable_scope)
`,is_package:!1},{filename:"home/tsiresy/work/python/nestipy/src/nestipy/ioc/container.py",lineno:220,name:"_resolve_method",code:`import inspect
from functools import lru_cache
from typing import Type, Union, Any, Optional, Callable, Awaitable, TYPE_CHECKING

from nestipy.metadata import ClassMetadata, CtxDepKey, ModuleMetadata, ProviderToken, Reflect
from .context_container import RequestContextContainer
from .dependency import TypeAnnotated
from .meta import ContainerHelper
from .utils import uniq

if TYPE_CHECKING:
    from .provider import ModuleProviderDict

_INIT = "__init__"


class NestipyContainer:
    _instance: "NestipyContainer" = None
    _services = {}
    _global_service_instances = {}
    _singleton_instances = {}
    _singleton_classes = set()
    helper = ContainerHelper()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(NestipyContainer, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def get_instance(cls, *args, **kwargs):
        return NestipyContainer(*args, **kwargs)

    def add_transient(self, service: Type):
        self._services[service] = service

    def add_singleton(self, service: Type):
        self._services[service] = service
        self._singleton_classes.add(service)

    def get_all_services(self) -> list:
        return list(self._services.keys())

    def add_singleton_instance(self, service: Union[Type, str], service_instance: object):
        self._singleton_instances[service] = service_instance

    def get_all_singleton_instance(self) -> list:
        return [v for k, v in self._singleton_instances.items()]

    @classmethod
    @lru_cache()
    def get_global_providers(cls) -> list:
        global_providers = []
        for service in cls._services:
            if service in global_providers:
                continue
            metadata: ClassMetadata = Reflect.get_metadata(service, ClassMetadata.Metadata, None)
            if metadata is not None:
                is_global = Reflect.get_metadata(metadata.get_module(), ModuleMetadata.Global, False)
                is_root = Reflect.get_metadata(metadata.get_module(), ModuleMetadata.Root, False)
                if is_global or is_root:
                    global_providers += Reflect.get_metadata(metadata.get_module(), ModuleMetadata.Providers, [])
        return uniq(global_providers)

    @classmethod
    def get_dependency_metadata(cls, service: Union[Type, object]) -> list:
        from .provider import ModuleProviderDict
        # extract global data from _service, not from module because all provider is already saved in _services of
        # container
        metadata: ClassMetadata = Reflect.get_metadata(service, ClassMetadata.Metadata, None)
        if metadata is not None:
            global_providers = cls.get_global_providers()
            providers, import_providers = metadata.get_service_providers()
            uniq_providers = []
            for m in uniq(providers + global_providers + import_providers):
                if isinstance(m, ModuleProviderDict):
                    uniq_providers.append(m.token)
                else:
                    uniq_providers.append(m)
            return uniq(uniq_providers)
        # raise ValueError(f"Dependency Metadata not found  for {service.__name__} service ")
        return []

    @classmethod
    async def _resolve_context_service(cls, name: str, dep_key: TypeAnnotated, annotation: Union[Type, Any]):
        context_container = RequestContextContainer.get_instance()
        callback = dep_key.metadata.callback
        if inspect.iscoroutinefunction(callback):
            return await callback(name, dep_key.metadata.token, annotation, context_container)
        else:
            return callback(name, dep_key.metadata.token, annotation, context_container)

    async def _resolve_module_provider_dict(self, instance: "ModuleProviderDict", search_scope: list):
        if instance.value:
            return instance.value
        elif instance.existing:
            if isinstance(instance.existing, ProviderToken):
                return await self.get(instance.existing.key)
            else:
                return await self.get(instance.existing)
        elif instance.use_class:
            return await self.get(instance.use_class)
        elif instance.factory:
            return await self.resolve_factory(
                factory=instance.factory,
                inject=instance.inject,
                search_scope=search_scope
            )

        else:
            return None

    async def _check_exist_singleton(self, key: Union[Type, str]):
        from .provider import ModuleProviderDict
        if key in self._singleton_instances:
            instance = self._singleton_instances[key]
            # to keep improve
            if isinstance(instance, ModuleProviderDict):
                search_scope = self.get_dependency_metadata(instance)
                if instance.token in search_scope:
                    value = await self._resolve_module_provider_dict(instance, search_scope=search_scope)
                    # update singleton instance to have the async value from ModuleProviderDict
                    self._singleton_instances[key] = value
                    return value
                else:
                    raise ValueError(
                        f"Service {instance.__class__.__name__} "
                        f"not found in scope")
            else:
                return instance
        return None

    def _check_service(self, key: Union[Type, str], origin: Optional[list] = None) -> tuple:
        if key not in self._services:
            raise ValueError(f"Service {key} not found")
        service = self._services[key]
        if service in (origin or []):
            raise ValueError(f"Circular dependency found  for {service.__name__} service ")
        return service, origin or set()

    async def _resolve_property(
            self,
            key: Union[Type, str],
            origin: Optional[list] = None,
            disable_scope: bool = False
    ):
        service, origin = self._check_service(key, origin)
        search_scope = self.get_dependency_metadata(service)
        origin.add(service)
        annotations: dict = getattr(service, '__annotations__', {})
        for name, param_annotation in annotations.items():
            annotation, dep_key = self.helper.get_type_from_annotation(param_annotation)
            if dep_key.metadata.key is not CtxDepKey.Service:
                dependency = await self._resolve_context_service(name, dep_key, annotation)
                setattr(service, name, dependency)
            elif dep_key.metadata.token in search_scope or annotation in search_scope or disable_scope:
                dependency = await self.get(dep_key.metadata.token or annotation)
                setattr(service, name, dependency)
            else:
                _name: str = annotation.__name__ if not isinstance(annotation, str) else annotation
                raise ValueError(f"Service {_name} not found in scope {search_scope}")
        origin.remove(service)
        self._services[key] = service

    async def _get_method_dependency(self, method_to_resolve: Callable, search_scope: list,
                                     disable_scope: bool = False):
        params = inspect.signature(method_to_resolve).parameters
        args = {}
        for name, param in params.items():
            if name != 'self' and param.annotation is not inspect.Parameter.empty:
                annotation, dep_key = self.helper.get_type_from_annotation(param.annotation)
                if dep_key.metadata.key is not CtxDepKey.Service:
                    dependency = await self._resolve_context_service(name, dep_key, annotation)
                    args[name] = dependency
                elif dep_key.metadata.token in search_scope or annotation in search_scope or disable_scope:
                    dependency = await self.get(dep_key.metadata.token or annotation)
                    args[name] = dependency
                else:
                    _name: str = annotation.__name__ if not isinstance(annotation, str) else annotation
                    raise ValueError(f"Service {_name} not found in scope {search_scope}")
        return args

    @classmethod
    async def _call_method(cls, method: Callable, args: dict):
        if inspect.iscoroutinefunction(method):
            return await method(**args)
        return method(**args)

    async def resolve_factory(self, factory: Callable, inject: list, search_scope: list, disable_scope: bool = False):
        search_scope_by_inject = [m for m in inject if m in search_scope]
        args = await self._get_method_dependency(
            method_to_resolve=factory,
            search_scope=search_scope_by_inject,
            disable_scope=disable_scope
        )
        return await self._call_method(method=factory, args=args)

    async def _resolve_method(
            self,
            key: Union[Type, str, object],
            method: str = _INIT,
            origin: Optional[list] = None,
            disable_scope: bool = False
    ):
        service, origin = self._check_service(key, origin)
        search_scope = self.get_dependency_metadata(service)
        origin.add(service)
        method_to_resolve = getattr(service, method, None)
        if not method_to_resolve:
            raise Exception(f"Method {method} not found in {service.__name__} service ")
        args = await self._get_method_dependency(method_to_resolve, search_scope, disable_scope=disable_scope)
        if method == _INIT:
            result = service(**args)
            if service in self._singleton_classes:
                self._singleton_instances[service] = result
        else:
            # Service must be an instance (controller)
            instance = await self.get(key)
            instance_method = getattr(instance, method, method_to_resolve)
            result = await self._call_method(instance_method, args)

        origin.remove(service)
        return result

    async def get(
            self,
            key: Union[Type, str],
            method: str = _INIT,
            origin: Optional[list] = None,
            disable_scope: Optional[bool] = False
    ) -> Awaitable[object]:
        in_singleton = await self._check_exist_singleton(key=key)
        if in_singleton:
            if method == _INIT:
                return in_singleton
        else:
            await self._resolve_property(key, origin=origin, disable_scope=disable_scope)
        return await self._resolve_method(key, method=method, origin=origin, disable_scope=disable_scope)
`,is_package:!1},{filename:"home/tsiresy/work/python/nestipy/src/nestipy/ioc/container.py",lineno:186,name:"_call_method",code:`import inspect
from functools import lru_cache
from typing import Type, Union, Any, Optional, Callable, Awaitable, TYPE_CHECKING

from nestipy.metadata import ClassMetadata, CtxDepKey, ModuleMetadata, ProviderToken, Reflect
from .context_container import RequestContextContainer
from .dependency import TypeAnnotated
from .meta import ContainerHelper
from .utils import uniq

if TYPE_CHECKING:
    from .provider import ModuleProviderDict

_INIT = "__init__"


class NestipyContainer:
    _instance: "NestipyContainer" = None
    _services = {}
    _global_service_instances = {}
    _singleton_instances = {}
    _singleton_classes = set()
    helper = ContainerHelper()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(NestipyContainer, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def get_instance(cls, *args, **kwargs):
        return NestipyContainer(*args, **kwargs)

    def add_transient(self, service: Type):
        self._services[service] = service

    def add_singleton(self, service: Type):
        self._services[service] = service
        self._singleton_classes.add(service)

    def get_all_services(self) -> list:
        return list(self._services.keys())

    def add_singleton_instance(self, service: Union[Type, str], service_instance: object):
        self._singleton_instances[service] = service_instance

    def get_all_singleton_instance(self) -> list:
        return [v for k, v in self._singleton_instances.items()]

    @classmethod
    @lru_cache()
    def get_global_providers(cls) -> list:
        global_providers = []
        for service in cls._services:
            if service in global_providers:
                continue
            metadata: ClassMetadata = Reflect.get_metadata(service, ClassMetadata.Metadata, None)
            if metadata is not None:
                is_global = Reflect.get_metadata(metadata.get_module(), ModuleMetadata.Global, False)
                is_root = Reflect.get_metadata(metadata.get_module(), ModuleMetadata.Root, False)
                if is_global or is_root:
                    global_providers += Reflect.get_metadata(metadata.get_module(), ModuleMetadata.Providers, [])
        return uniq(global_providers)

    @classmethod
    def get_dependency_metadata(cls, service: Union[Type, object]) -> list:
        from .provider import ModuleProviderDict
        # extract global data from _service, not from module because all provider is already saved in _services of
        # container
        metadata: ClassMetadata = Reflect.get_metadata(service, ClassMetadata.Metadata, None)
        if metadata is not None:
            global_providers = cls.get_global_providers()
            providers, import_providers = metadata.get_service_providers()
            uniq_providers = []
            for m in uniq(providers + global_providers + import_providers):
                if isinstance(m, ModuleProviderDict):
                    uniq_providers.append(m.token)
                else:
                    uniq_providers.append(m)
            return uniq(uniq_providers)
        # raise ValueError(f"Dependency Metadata not found  for {service.__name__} service ")
        return []

    @classmethod
    async def _resolve_context_service(cls, name: str, dep_key: TypeAnnotated, annotation: Union[Type, Any]):
        context_container = RequestContextContainer.get_instance()
        callback = dep_key.metadata.callback
        if inspect.iscoroutinefunction(callback):
            return await callback(name, dep_key.metadata.token, annotation, context_container)
        else:
            return callback(name, dep_key.metadata.token, annotation, context_container)

    async def _resolve_module_provider_dict(self, instance: "ModuleProviderDict", search_scope: list):
        if instance.value:
            return instance.value
        elif instance.existing:
            if isinstance(instance.existing, ProviderToken):
                return await self.get(instance.existing.key)
            else:
                return await self.get(instance.existing)
        elif instance.use_class:
            return await self.get(instance.use_class)
        elif instance.factory:
            return await self.resolve_factory(
                factory=instance.factory,
                inject=instance.inject,
                search_scope=search_scope
            )

        else:
            return None

    async def _check_exist_singleton(self, key: Union[Type, str]):
        from .provider import ModuleProviderDict
        if key in self._singleton_instances:
            instance = self._singleton_instances[key]
            # to keep improve
            if isinstance(instance, ModuleProviderDict):
                search_scope = self.get_dependency_metadata(instance)
                if instance.token in search_scope:
                    value = await self._resolve_module_provider_dict(instance, search_scope=search_scope)
                    # update singleton instance to have the async value from ModuleProviderDict
                    self._singleton_instances[key] = value
                    return value
                else:
                    raise ValueError(
                        f"Service {instance.__class__.__name__} "
                        f"not found in scope")
            else:
                return instance
        return None

    def _check_service(self, key: Union[Type, str], origin: Optional[list] = None) -> tuple:
        if key not in self._services:
            raise ValueError(f"Service {key} not found")
        service = self._services[key]
        if service in (origin or []):
            raise ValueError(f"Circular dependency found  for {service.__name__} service ")
        return service, origin or set()

    async def _resolve_property(
            self,
            key: Union[Type, str],
            origin: Optional[list] = None,
            disable_scope: bool = False
    ):
        service, origin = self._check_service(key, origin)
        search_scope = self.get_dependency_metadata(service)
        origin.add(service)
        annotations: dict = getattr(service, '__annotations__', {})
        for name, param_annotation in annotations.items():
            annotation, dep_key = self.helper.get_type_from_annotation(param_annotation)
            if dep_key.metadata.key is not CtxDepKey.Service:
                dependency = await self._resolve_context_service(name, dep_key, annotation)
                setattr(service, name, dependency)
            elif dep_key.metadata.token in search_scope or annotation in search_scope or disable_scope:
                dependency = await self.get(dep_key.metadata.token or annotation)
                setattr(service, name, dependency)
            else:
                _name: str = annotation.__name__ if not isinstance(annotation, str) else annotation
                raise ValueError(f"Service {_name} not found in scope {search_scope}")
        origin.remove(service)
        self._services[key] = service

    async def _get_method_dependency(self, method_to_resolve: Callable, search_scope: list,
                                     disable_scope: bool = False):
        params = inspect.signature(method_to_resolve).parameters
        args = {}
        for name, param in params.items():
            if name != 'self' and param.annotation is not inspect.Parameter.empty:
                annotation, dep_key = self.helper.get_type_from_annotation(param.annotation)
                if dep_key.metadata.key is not CtxDepKey.Service:
                    dependency = await self._resolve_context_service(name, dep_key, annotation)
                    args[name] = dependency
                elif dep_key.metadata.token in search_scope or annotation in search_scope or disable_scope:
                    dependency = await self.get(dep_key.metadata.token or annotation)
                    args[name] = dependency
                else:
                    _name: str = annotation.__name__ if not isinstance(annotation, str) else annotation
                    raise ValueError(f"Service {_name} not found in scope {search_scope}")
        return args

    @classmethod
    async def _call_method(cls, method: Callable, args: dict):
        if inspect.iscoroutinefunction(method):
            return await method(**args)
        return method(**args)

    async def resolve_factory(self, factory: Callable, inject: list, search_scope: list, disable_scope: bool = False):
        search_scope_by_inject = [m for m in inject if m in search_scope]
        args = await self._get_method_dependency(
            method_to_resolve=factory,
            search_scope=search_scope_by_inject,
            disable_scope=disable_scope
        )
        return await self._call_method(method=factory, args=args)

    async def _resolve_method(
            self,
            key: Union[Type, str, object],
            method: str = _INIT,
            origin: Optional[list] = None,
            disable_scope: bool = False
    ):
        service, origin = self._check_service(key, origin)
        search_scope = self.get_dependency_metadata(service)
        origin.add(service)
        method_to_resolve = getattr(service, method, None)
        if not method_to_resolve:
            raise Exception(f"Method {method} not found in {service.__name__} service ")
        args = await self._get_method_dependency(method_to_resolve, search_scope, disable_scope=disable_scope)
        if method == _INIT:
            result = service(**args)
            if service in self._singleton_classes:
                self._singleton_instances[service] = result
        else:
            # Service must be an instance (controller)
            instance = await self.get(key)
            instance_method = getattr(instance, method, method_to_resolve)
            result = await self._call_method(instance_method, args)

        origin.remove(service)
        return result

    async def get(
            self,
            key: Union[Type, str],
            method: str = _INIT,
            origin: Optional[list] = None,
            disable_scope: Optional[bool] = False
    ) -> Awaitable[object]:
        in_singleton = await self._check_exist_singleton(key=key)
        if in_singleton:
            if method == _INIT:
                return in_singleton
        else:
            await self._resolve_property(key, origin=origin, disable_scope=disable_scope)
        return await self._resolve_method(key, method=method, origin=origin, disable_scope=disable_scope)
`,is_package:!1},{filename:"app_controller.py",lineno:104,name:"test",code:`import dataclasses
import os.path
import shutil
from typing import Any, Annotated, Optional, Type

from pydantic import BaseModel

from app_provider import AppProvider
from nestipy.common import Controller, Injectable, Post, Get, logger, UploadFile, HttpStatus, HttpStatusMessages
from nestipy.common import ExceptionFilter, Catch, UseFilters
from nestipy.common import HttpException, apply_decorators
from nestipy.common import NestipyInterceptor, UseInterceptors, Render
from nestipy.common import Request, Response
from nestipy.core import ArgumentHost, ExecutionContext
from nestipy.ioc import Inject, Req, Res, Body, Cookie, Session, Header, create_type_annotated, RequestContextContainer
from nestipy.openapi import ApiResponse, ApiParameter, ApiConsumer
from nestipy.openapi import ApiTags, ApiOkResponse, ApiNotFoundResponse, ApiCreatedResponse, NoSwagger, ApiBody
from nestipy.openapi.openapi_docs.v3 import Parameter, ParameterLocation, Schema
from nestipy.types_ import NextFn


def user_callback(_name: str, _token: Optional[str], _type_ref: Type, _request_context: RequestContextContainer):
    return "User"


User = create_type_annotated(user_callback, "user")


class Test2(BaseModel):
    name2: str


@dataclasses.dataclass
class Test3:
    name3: str


class TestBody(BaseModel):
    image: UploadFile
    test2: Test2
    test3: Test3


class UnauthorizedResponse(BaseModel):
    status: int = 401
    message: str
    details: str


@Catch()
class HttpExceptionFilter(ExceptionFilter):
    async def catch(self, exception: HttpException, host: ArgumentHost) -> Any:
        print('Catcher')


@Catch()
class Http2ExceptionFilter(ExceptionFilter):
    async def catch(self, exception: HttpException, host: ArgumentHost) -> Any:
        print('Catcher2')
        return None


@Injectable()
class TestInterceptor(NestipyInterceptor):
    async def intercept(self, context: ExecutionContext, next_fn: NextFn):
        return await next_fn()


@Injectable()
class TestMethodInterceptor(NestipyInterceptor):
    async def intercept(self, context: ExecutionContext, next_fn: NextFn):
        return await next_fn()


def ApiDecorator():
    return apply_decorators(
        ApiNotFoundResponse(UnauthorizedResponse),
        UseInterceptors(TestInterceptor)
    )


@Controller()
@ApiTags('App')
@ApiDecorator()
@UseFilters(Http2ExceptionFilter)
class AppController:
    provider: Annotated[AppProvider, Inject()]

    @NoSwagger()
    @Render('index.html')
    @Get()
    async def test(
            self,
            req: Annotated[Request, Req()],
            res: Annotated[Response, Res()],
            headers: Annotated[dict, Header()],
            cookies: Annotated[dict, Cookie()],
            user_id: Annotated[str, Session('user_id')],
            sessions: Annotated[dict, Session()]
    ):
        # req.session['user_id'] = 2
        # res.cookie('test', 'test-cookie')
        logger.info(sessions)
        raise HttpException(HttpStatus.UNAUTHORIZED, HttpStatusMessages.UNAUTHORIZED)
        # return {'title': 'Hello'}
        # return await res.render('index.html', {'title': 'Hello'})

    @Post()
    @ApiBody(TestBody, ApiConsumer.MULTIPART)
    @ApiCreatedResponse()
    @ApiResponse(401, UnauthorizedResponse)
    @ApiOkResponse()
    @UseInterceptors(TestMethodInterceptor)
    @ApiParameter(
        Parameter(in_=ParameterLocation.QUERY, name="param", schema=Schema(type="string"))
    )
    @UseFilters(HttpExceptionFilter)
    async def post(
            self,
            res: Annotated[Response, Res()],
            user: Annotated[str, User()],
            body: Annotated[TestBody, Body('latin-1')]
    ):
        print(user)
        file_path = os.path.join(os.path.dirname(__file__), f"nestipy_{body.image.filename}")
        file = open(file_path, "wb")
        shutil.copyfileobj(body.image.file, file)
        file.close()
        return {"uploaded": "Ok"}
        # raise HttpException(HttpStatus.UNAUTHORIZED, HttpStatusMessages.UNAUTHORIZED)
`,is_package:!0}],Im={python:"3.11.6",nestipy:"1.0.0a2"},Fm={exception:Cm,type:Nm,message:Rm,root:Tm,request:Am,traceback:Pm,framework:Im};function Om(){const[e,n]=z.useState(void 0),[t,r]=ze.useState(),o=z.useCallback(i=>{const a=document.getElementById("code-block"),s=document.getElementById(i);console.log(s.offsetTop),a.scrollTo({top:s.offsetTop-300,left:0,behavior:"instant"})},[]);return z.useEffect(()=>{t&&e&&o(`${e.root}/${t.filename}-${t.lineno}`)},[o,e,t]),z.useEffect(()=>{const i=document.getElementById("error-data");if(i){const a=JSON.parse(i.getAttribute("data-json")??""),s=a.traceback;console.log(s.reverse()[0]),r(s[0]),n(a)}},[]),I.jsxs("div",{className:"w-full flex-1 flex items-center flex-col py-12 gap-y-10 px-4 ",children:[I.jsx("div",{id:"error-data","data-json":JSON.stringify(Fm)}),I.jsxs("div",{className:"flex flex-1 max-w-[1200px] w-full justify-between rounded-md gap-x-5b items-center lg:items-center ",children:[I.jsxs("div",{className:"w-auto flex-1 items-center flex gap-x-5",children:[I.jsx("div",{className:"flex rounded-[50px] w-[50px] h-[50px] bg-red-800/30 justify-center items-center",children:I.jsx(Sm,{className:"text-red-400",size:20})}),I.jsx("div",{className:"font-bold capitalize text-xl",children:e==null?void 0:e.exception})]}),I.jsx("div",{className:"pr-3",children:I.jsx("img",{src:bm,height:30,width:30,alt:"Logo"})})]}),I.jsxs("div",{className:"gap-y-6 lg:gap-0 flex flex-col lg:flex-row flex-1 max-w-[1200px] w-full py-8 justify-between bg-gray-900/80 px-8 rounded-md gap-x-5b border border-gray-800",children:[I.jsxs("div",{className:"flex-1 flex flex-col gap-y-4 items-start  ",children:[I.jsx("div",{className:"capitalize bg-red-800/30 px-4 py-1 rounded-3xl text-red-600 text-sm",children:e==null?void 0:e.type}),I.jsx("div",{className:"font-bold capitalize text-lg px-4 break-words text-wrap",children:e==null?void 0:e.message})]}),I.jsxs("div",{className:"flex flex-col gap-y-4 items-start lg:items-end text-sm",children:[I.jsxs("div",{className:"px-4 text-gray-200 bg-gray-400/10 py-2 rounded-3xl text-sm",children:[e==null?void 0:e.request.method.toUpperCase()," ",e==null?void 0:e.request.host]}),I.jsxs("div",{className:"capitalize px-4 text-green-700",children:["Python ",e==null?void 0:e.framework.python,"  —  Nestipy ",e==null?void 0:e.framework.nestipy]})]})]}),I.jsxs("div",{className:"flex flex-1 flex-col lg:flex-row gap-x-5 max-w-[1200px] w-full bg-gray-900/80 py-8 px-8 lg:p-8  border border-gray-800 rounded-md",children:[I.jsx("div",{className:"w-full lg:w-[300px] py-6 lg:p-6 rounded-md text-gray-300 text-sm flex flex-col gap-y-2 max-h-[600px] scrollbar-none overflow-y-auto",children:((e==null?void 0:e.traceback)??[]).map(i=>I.jsx("div",{onClick:()=>r(i),className:JSON.stringify(i)!==JSON.stringify(t)?"cursor-pointer w-full p-3 rounded-sm bg-gray-800/20 text-wrap break-words":"text-wrap break-words border-l-2 border-l-red-800 border border-gray-800 py-5 cursor-pointer w-full p-3 rounded-sm bg-gray-800/20 text-gray-200",children:I.jsxs("span",{children:[i.filename," :",i.lineno]})},`${i.is_package?"":(e==null?void 0:e.root)+"/"}${i.filename}-${i.lineno}`))}),I.jsx("div",{className:"flex flex-col flex-1 w-full lg:w-3/5 gap-y-6",children:t&&I.jsx(hn,{theme:Nc.dracula,code:t.code,lines:[t.lineno],language:"python",children:I.jsxs("div",{className:" relative !bg-gray-800/40 rounded-lg  shadow-md text-sm ",children:[I.jsxs("div",{className:"text-sm text-gray-400 px-8 py-6 break-words text-wrap",children:[t.is_package?"":(e==null?void 0:e.root)+"/",t.filename," :",t.lineno]}),I.jsx(hn.Code,{id:"code-block",className:"!px-0 max-h-[500px] overflow-auto scrollbar-none text-gray-100",children:({isLineHighlighted:i,lineNumber:a})=>I.jsxs("div",{className:`table-row ${i?"bg-red-700/20":"opacity-60"}`,...a===t.lineno?{id:`${e==null?void 0:e.root}/${t.filename}-${t.lineno}`}:{},children:[I.jsx("span",{className:"table-cell pl-6 pr-4 text-sm text-right select-none text-gray-200",children:a}),I.jsx(hn.LineContent,{className:"table-cell w-full pr-6 py-1",children:I.jsx(hn.Token,{})})]})}),I.jsx("div",{className:"text-sm text-gray-500 px-6 pb-4 text-right uppercase select-none pt-4 ",children:"python"})]})})})]})]})}ii.createRoot(document.getElementById("root")).render(I.jsx(ze.StrictMode,{children:I.jsx(Om,{})}));
