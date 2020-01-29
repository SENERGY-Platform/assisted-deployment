"use strict";

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