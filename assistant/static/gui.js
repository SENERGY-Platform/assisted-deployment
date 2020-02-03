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
    response_pane.style.display = "none";
    loader.style.display = "flex";
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
    loader.style.display = "none";
    response_pane.style.display = "block";
    return response || err;
}


function clearContainer(container) {
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }
}


function clearResponsePane() {
    while (response_pane.firstChild) {
        response_pane.removeChild(response_pane.firstChild);
    }
}


let param_map = {
    0: 'project=',
    1: '&namespace=',
    2: '&workload='
};

async function kubectl(cmd, params) {
    let request_params = "";
    for (let i = 0; i < params.length; i++) {
        request_params += param_map[i] + params[i];
    }
    let result = await awaitRequest("GET", "../kubectl/"+cmd+"?"+request_params);
    if (result.status === 200) {
        clearResponsePane();
        response_pane.appendChild(document.createTextNode(result.response));
    }
}


async function rancherCli(cmd, params) {
    let request_params = "";
    for (let i = 0; i < params.length; i++) {
        request_params += param_map[i] + params[i];
    }
    let result = await awaitRequest("GET", "../rancher/"+cmd+"?"+request_params);
    if (result.status === 200) {
        clearResponsePane();
        response_pane.appendChild(document.createTextNode(result.response));
    }
}


function addRancherCliBtns(item, path, element) {
    let params = path.split("/");
    params.push(item);
    params = params.filter(item => item);

    let create_btn = document.createElement('button');
    create_btn.type = 'button';
    create_btn.className = 'btn';
    create_btn.appendChild(document.createTextNode('create'));
    create_btn.onclick = async function () {
        if (confirm("CREATE --> '" + item + "' ?")) {
            rancherCli('create', params)
        }
    };
    element.appendChild(create_btn);

    let delete_btn = document.createElement('button');
    delete_btn.type = 'button';
    delete_btn.className = 'btn';
    delete_btn.appendChild(document.createTextNode('delete'));
    delete_btn.onclick = async function () {
        if (confirm("DELETE --> '" + item + "' ?")) {
            rancherCli('delete', params)
        }
    };
    element.appendChild(delete_btn);
}


function addKubectlBtns(item, path, element) {
    let params = path.split("/");
    params.push(item);
    params = params.filter(item => item);

    let create_btn = document.createElement('button');
    create_btn.type = 'button';
    create_btn.className = 'btn';
    create_btn.appendChild(document.createTextNode('create'));
    create_btn.onclick = async function () {
        if (confirm("CREATE --> '" + item + "' ?")) {
            kubectl('create', params)
        }
    };
    element.appendChild(create_btn);

    let delete_btn = document.createElement('button');
    delete_btn.type = 'button';
    delete_btn.className = 'btn';
    delete_btn.appendChild(document.createTextNode('delete'));
    delete_btn.onclick = async function () {
        if (confirm("DELETE --> '" + item + "' ?")) {
            kubectl('delete', params)
        }
    };
    element.appendChild(delete_btn);

    let apply_btn = document.createElement('button');
    apply_btn.type = 'button';
    apply_btn.className = 'btn';
    apply_btn.appendChild(document.createTextNode('apply'));
    apply_btn.onclick = async function () {
        if (confirm("APPLY --> '" + item + "' ?")) {
            kubectl('apply', params)
        }
    };
    element.appendChild(apply_btn);
}


async function listItems(grid, level, path="") {
    let containers = [];
    containers.push(grid.getElementsByClassName('projects')[0]);
    containers.push(grid.getElementsByClassName('namespaces')[0]);
    containers.push(grid.getElementsByClassName('workloads')[0]);
    containers = containers.filter(item => item);
    let items = [];
    let result = await awaitRequest("GET", "../projects"+path);
    if (result.status === 200) {
        items = JSON.parse(result.response);
    }
    if (containers.length === 3 && level - 1 === 0) {
        clearContainer(containers[2])
    }
    clearContainer(containers[level]);
    for (let item of items) {
        let container_div = document.createElement('div');
        container_div.className = 'deployment-item-container';
        let top_div = document.createElement('div');
        top_div.className = 'deployment-item-container-top';
        let bottom_div = document.createElement('div');
        bottom_div.className = 'deployment-item-container-bottom';

        top_div.appendChild(document.createTextNode(item));

        switch (grid) {
            case rancher_grid:
                addRancherCliBtns(item, path, bottom_div);
                break;
            case kubectl_grid:
                addKubectlBtns(item, path, bottom_div);
                break;
            // case helm_grid:
            //     console.log("helm");
            //     break;
        }

        if (level < containers.length - 1) {
            let expand_btn = document.createElement('button');
            expand_btn.type = 'button';
            expand_btn.className = 'btn';
            expand_btn.appendChild(document.createTextNode('expand'));
            expand_btn.onclick = function () {
                for (let cd of containers[level].getElementsByClassName('deployment-item-container-active')) {
                    cd.className = 'deployment-item-container';
                }
                container_div.className = 'deployment-item-container-active';
                listItems(grid,level + 1, path + "/" + item);
            };
            bottom_div.appendChild(expand_btn);
        }

        container_div.appendChild(top_div);
        container_div.appendChild(bottom_div);

        containers[level].appendChild(container_div);
    }
}

async function listVersions(pane) {
    let endpoints = ["/rancher/version", "/kubectl/version", "/helm/version"];
    for (let endpoint of endpoints) {
        pane.appendChild(document.createTextNode(endpoint.split("/")[1] + ":"));
        pane.appendChild(document.createElement('br'));
        let result = await awaitRequest("GET", ".." + endpoint);
        if (result.status === 200) {
            pane.appendChild(document.createTextNode(result.response));
        }
        pane.appendChild(document.createElement('br'));
        pane.appendChild(document.createElement('br'));
        pane.appendChild(document.createElement('br'));
    }
}

function addSaveBtn(pane, data_element, path) {
    let save_btn = document.createElement('button');
    save_btn.type = 'button';
    save_btn.className = 'btn';
    save_btn.appendChild(document.createTextNode('save'));
    save_btn.onclick = async function () {
        let result = await awaitRequest("PUT", ".." + path, "text/plain; charset=utf-8", data_element.value);
        clearResponsePane();
        response_pane.appendChild(document.createTextNode(result.status));
    };
    pane.appendChild(save_btn);
}

async function showConfigItem(pane, path) {
    let textarea = document.createElement('textarea');
    textarea.className = "text-box";
    let result = await awaitRequest("GET", ".." + path);
    if (result.status === 200) {
        textarea.value = result.response
    }
    pane.appendChild(textarea);
    addSaveBtn(pane, textarea, path);
}

