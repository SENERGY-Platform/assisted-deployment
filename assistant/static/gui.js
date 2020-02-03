"use strict";


/*
Copyright 2020 InfAI (CC SES)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/


let loader;
let kubectl_grid;
let rancher_grid;
// let helm_grid;
let configuration_grid;
let response_pane;
let content_pane;


window.addEventListener("DOMContentLoaded", function (e) {
    loader = document.getElementById('sk-wave');
    rancher_grid = document.getElementById('rancher');
    kubectl_grid = document.getElementById('kubectl');
    // helm_grid = document.getElementById('helm');
    configuration_grid = document.getElementById('configuration');
    response_pane = document.getElementById('response');
    content_pane = document.getElementById('content');
});


function httpPut(uri, header, body) {
    if (uri) {
        return new Promise(function (resolve, reject) {
            let request = new XMLHttpRequest();
            request.open("PUT", uri, true);
            if (header) {
                request.setRequestHeader(header[0], header[1]);
            }
            request.timeout = 25000;
            request.onreadystatechange = function () {
                if (request.readyState === 4) {
                    if (request.status === 200) {
                        resolve(request);
                    } else {
                        reject(request);
                    }
                }
            };
            request.ontimeout = function () {
                reject(request);
            };
            if (body) {
                request.send(body);
            } else {
                request.send();
            }
        })
    }
}

function httpGet(uri, header) {
    if (uri) {
        return new Promise(function (resolve, reject) {
            let request = new XMLHttpRequest();
            request.open("GET", uri, true);
            if (header) {
                request.setRequestHeader(header);
            }
            request.timeout = 25000;
            request.onreadystatechange = function () {
                if (request.readyState === 4) {
                    if (request.status === 200) {
                        resolve(request);
                    } else {
                        reject(request);
                    }
                }
            };
            request.ontimeout = function () {
                reject(request);
            };
            request.send();
        })
    }
}

async function awaitRequest(method, uri, content_type, body, header) {
    let response;
    let err;
    //loader.style.display = "block";
    if (method === 'GET') {
        response = await httpGet(uri, header).catch(function (e) {
            err = e;
        });
    }
    if (method === 'PUT') {
        response = await httpPut(uri, content_type, body).catch(function (e) {
            err = e;
        });
    }
    //loader.style.display = "none";
    return response || err;
}

async function getProjects() {
    let result = await awaitRequest("GET", "projects");
    if (result.status === 200) {
        console.log(result.response);
    }
    return false;
}

window.addEventListener("DOMContentLoaded", function (e) {
   getProjects();
});