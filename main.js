import * as THREE from "three";

// renderer
const canvas = document.querySelector("#c");
const renderer = new THREE.WebGLRenderer({ canvas });
renderer.setSize(window.innerWidth, window.innerHeight);

// scene
const scene = new THREE.Scene();

// camera
const camera = new THREE.PerspectiveCamera(
  60,
  window.innerWidth / window.innerHeight,
  0.1,
  100
);
camera.position.z = 3;

// light
const light = new THREE.PointLight(0xffffff, 2);
light.position.set(2, 2, 2);
scene.add(light);

// geometry
const geometry = new THREE.SphereGeometry(1, 128, 128);

// shader material
const material = new THREE.ShaderMaterial({
  uniforms: {
    time: { value: 0 },
    amp: { value: 0.3 }
  },

  vertexShader: `
    uniform float time;
    uniform float amp;

    void main() {
      vec3 pos = position;

      float wave =
        sin(pos.x * 10.0 + time) *
        sin(pos.y * 10.0 + time) *
        sin(pos.z * 10.0 + time);

      pos += normal * wave * amp;

      gl_Position = projectionMatrix *
                    modelViewMatrix *
                    vec4(pos, 1.0);
    }
  `,

  fragmentShader: `
    void main() {
      gl_FragColor = vec4(0.2, 0.6, 1.0, 1.0);
    }
  `
});

// mesh
const bubble = new THREE.Mesh(geometry, material);
scene.add(bubble);

// animation loop
function animate(t) {
  material.uniforms.time.value = t * 0.001;
  bubble.rotation.y += 0.002;

  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

animate(0);

// resize
window.addEventListener("resize", () => {
  renderer.setSize(window.innerWidth, window.innerHeight);
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
});console.log("JS connected");console.log("JS connected");
console.log("JS connected");