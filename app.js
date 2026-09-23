import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js";
import {OrbitControls} from "https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/controls/OrbitControls.js";
import {TransformControls} from "https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/controls/TransformControls.js";
import {GLTFLoader} from "https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/loaders/GLTFLoader.js";
import {GLTFExporter} from "https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/exporters/GLTFExporter.js";
import {parseBlend,extractMeshes,extractObjects,extractMaterials} from "https://esm.sh/jsblender@0.2.0?bundle";

const viewport=document.querySelector("#viewport"),status=document.querySelector("#status"),selected=document.querySelector("#selected"),file=document.querySelector("#file");
const scene=new THREE.Scene();scene.background=new THREE.Color(0x0e1015);
const camera=new THREE.PerspectiveCamera(45,1,.01,100000);camera.position.set(4,3,6);
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;viewport.appendChild(renderer.domElement);
const orbit=new OrbitControls(camera,renderer.domElement);orbit.enableDamping=true;
scene.add(new THREE.HemisphereLight(0xffffff,0x39404d,2.2));const key=new THREE.DirectionalLight(0xffffff,3);key.position.set(5,8,5);scene.add(key);
scene.add(new THREE.GridHelper(20,20,0x39414e,0x202631));
const root=new THREE.Group();root.name="Model";scene.add(root);
const transform=new TransformControls(camera,renderer.domElement);transform.setMode("translate");transform.addEventListener("dragging-changed",e=>orbit.enabled=!e.value);scene.add(transform);
const ray=new THREE.Raycaster(),mouse=new THREE.Vector2();let selectedObj=null,wire=false;
function resize(){const r=viewport.getBoundingClientRect();camera.aspect=r.width/r.height;camera.updateProjectionMatrix();renderer.setSize(r.width,r.height,false)}addEventListener("resize",resize);resize();
function clear(){while(root.children.length){const o=root.children.pop();o.traverse(x=>{if(x.geometry)x.geometry.dispose()})}transform.detach();selectedObj=null;selected.textContent="Nothing selected"}
function fit(){const box=new THREE.Box3().setFromObject(root);if(box.isEmpty())return;const s=box.getSize(new THREE.Vector3()).length(),c=box.getCenter(new THREE.Vector3());camera.position.copy(c).add(new THREE.Vector3(s*.8,s*.55,s*.8));camera.near=Math.max(s/10000,.001);camera.far=Math.max(s*100,1000);camera.updateProjectionMatrix();orbit.target.copy(c);orbit.update()}
function select(o){selectedObj=o;selected.textContent=o?.name||"Object";if(o){transform.attach(o);px.value=o.position.x;py.value=o.position.y;pz.value=o.position.z;scale.value=o.scale.x;}}
const px=document.querySelector("#px"),py=document.querySelector("#py"),pz=document.querySelector("#pz"),scale=document.querySelector("#scale"),color=document.querySelector("#color");
function sync(){if(!selectedObj)return;selectedObj.position.set(+px.value||0,+py.value||0,+pz.value||0);const s=Math.max(.01,+scale.value||1);selectedObj.scale.setScalar(s);selectedObj.traverse(o=>{if(o.material?.color)o.material.color.set(color.value)})}
[px,py,pz,scale,color].forEach(x=>x.addEventListener("input",sync));
document.querySelector("#fit").onclick=fit;
document.querySelector("#reset").onclick=()=>{camera.position.set(4,3,6);orbit.target.set(0,0,0);orbit.update()};
document.querySelector("#wire").onclick=()=>{wire=!wire;root.traverse(o=>{if(o.material){const a=Array.isArray(o.material)?o.material:[o.material];a.forEach(m=>m.wireframe=wire)}})};
renderer.domElement.addEventListener("pointerdown",e=>{const r=renderer.domElement.getBoundingClientRect();mouse.x=((e.clientX-r.left)/r.width)*2-1;mouse.y=-((e.clientY-r.top)/r.height)*2+1;ray.setFromCamera(mouse,camera);const hit=ray.intersectObjects(root.children,true)[0];if(hit){let o=hit.object;while(o.parent&&o.parent!==root)o=o.parent;select(o)}});
function loadGLB(buf,name){clear();new GLTFLoader().parse(buf,"",g=>{root.add(g.scene);status.textContent=name+" loaded. Select objects to edit.";fit()},e=>{status.textContent="Could not open model: "+e.message})}
function loadBlend(buf,name){clear();status.textContent="Reading Blender file…";try{const b=parseBlend(new Uint8Array(buf));const meshes=extractMeshes(b),objects=extractObjects(b),mats=extractMaterials(b);const matMap=new Map(mats.map(m=>[m.name,m]));const meshMap=new Map();
for(const m of meshes){const g=new THREE.BufferGeometry();g.setAttribute("position",new THREE.BufferAttribute(m.vertices,3));g.setIndex(new THREE.BufferAttribute(m.triangles,1));g.computeVertexNormals();meshMap.set(m.name,g)}
for(const o of objects){if(o.type!==1||!o.dataName||!meshMap.has(o.dataName))continue;const g=meshMap.get(o.dataName).clone(),md=meshes.find(x=>x.name===o.dataName);let col=new THREE.Color(0x8ab4ff);const mn=md?.materialSlotNames?.[0];if(mn&&matMap.has(mn)){const c=matMap.get(mn).diffuse;col.setRGB(c[0],c[1],c[2])}const mesh=new THREE.Mesh(g,new THREE.MeshStandardMaterial({color:col,roughness:.65,metalness:.05}));mesh.name=o.name;mesh.position.set(...o.location);mesh.rotation.set(...o.rotation);mesh.scale.set(...o.scale);root.add(mesh)}
status.textContent=name+" loaded. Edit objects, then export GLB.";fit()}catch(e){status.textContent="This .blend could not be parsed: "+e.message}}
file.onchange=()=>file.files[0]&&openFile(file.files[0]);
async function openFile(f){status.textContent="Opening "+f.name+"…";const buf=await f.arrayBuffer();const ext=f.name.toLowerCase().split(".").pop();if(ext==="blend")loadBlend(buf,f.name);else loadGLB(buf,f.name)}
viewport.addEventListener("dragover",e=>{e.preventDefault();viewport.classList.add("dragover")});
viewport.addEventListener("dragleave",()=>viewport.classList.remove("dragover"));
viewport.addEventListener("drop",e=>{e.preventDefault();viewport.classList.remove("dragover");if(e.dataTransfer.files[0])openFile(e.dataTransfer.files[0])});
document.querySelector("#export").onclick=()=>{new GLTFExporter().parse(root,g=>{const blob=new Blob([g],{type:"model/gltf-binary"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="3d-canva-edited.glb";a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)},e=>{status.textContent="Export failed: "+e.message},{binary:true,onlyVisible:false})};
document.querySelector("#save").onclick=()=>{localStorage.setItem("3dcanva-settings",JSON.stringify({wire}));status.textContent="Project settings saved on this device."};
function animate(){requestAnimationFrame(animate);orbit.update();renderer.render(scene,camera)}animate();