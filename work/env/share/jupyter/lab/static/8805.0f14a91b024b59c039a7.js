"use strict";(self["webpackChunk_jupyterlab_application_top"]=self["webpackChunk_jupyterlab_application_top"]||[]).push([[8805],{78805:(e,t,n)=>{n.r(t);n.d(t,{turtle:()=>p});var r;function i(e){return new RegExp("^(?:"+e.join("|")+")$","i")}var l=i([]);var a=i(["@prefix","@base","a"]);var o=/[*+\-<>=&|]/;function c(e,t){var n=e.next();r=null;if(n=="<"&&!e.match(/^[\s\u00a0=]/,false)){e.match(/^[^\s\u00a0>]*>?/);return"atom"}else if(n=='"'||n=="'"){t.tokenize=u(n);return t.tokenize(e,t)}else if(/[{}\(\),\.;\[\]]/.test(n)){r=n;return null}else if(n=="#"){e.skipToEnd();return"comment"}else if(o.test(n)){e.eatWhile(o);return null}else if(n==":"){return"operator"}else{e.eatWhile(/[_\w\d]/);if(e.peek()==":"){return"variableName.special"}else{var i=e.current();if(a.test(i)){return"meta"}if(n>="A"&&n<="Z"){return"comment"}else{return"keyword"}}var i=e.current();if(l.test(i))return null;else if(a.test(i))return"meta";else return"variable"}}function u(e){return function(t,n){var r=false,i;while((i=t.next())!=null){if(i==e&&!r){n.tokenize=c;break}r=!r&&i=="\\"}return"string"}}function s(e,t,n){e.context={prev:e.context,indent:e.indent,col:n,type:t}}function f(e){e.indent=e.context.indent;e.context=e.context.prev}const p={name:"turtle",startState:function(){return{tokenize:c,context:null,indent:0,col:0}},token:function(e,t){if(e.sol()){if(t.context&&t.context.align==null)t.context.align=false;t.indent=e.indentation()}if(e.eatSpace())return null;var n=t.tokenize(e,t);if(n!="comment"&&t.context&&t.context.align==null&&t.context.type!="pattern"){t.context.align=true}if(r=="(")s(t,")",e.column());else if(r=="[")s(t,"]",e.column());else if(r=="{")s(t,"}",e.column());else if(/[\]\}\)]/.test(r)){while(t.context&&t.context.type=="pattern")f(t);if(t.context&&r==t.context.type)f(t)}else if(r=="."&&t.context&&t.context.type=="pattern")f(t);else if(/atom|string|variable/.test(n)&&t.context){if(/[\}\]]/.test(t.context.type))s(t,"pattern",e.column());else if(t.context.type=="pattern"&&!t.context.align){t.context.align=true;t.context.col=e.column()}}return n},indent:function(e,t,n){var r=t&&t.charAt(0);var i=e.context;if(/[\]\}]/.test(r))while(i&&i.type=="pattern")i=i.prev;var l=i&&r==i.type;if(!i)return 0;else if(i.type=="pattern")return i.col;else if(i.align)return i.col+(l?0:1);else return i.indent+(l?0:n.unit)},languageData:{commentTokens:{line:"#"}}}}}]);