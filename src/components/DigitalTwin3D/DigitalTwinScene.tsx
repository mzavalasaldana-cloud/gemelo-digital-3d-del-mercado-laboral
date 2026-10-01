import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';
import { 
  CountryCode, 
  WorkerAgent, 
  StructuralFirm, 
  ScenarioPreset,
  PolicyParameters,
  AppTheme
} from '../../types';
import { COUNTRY_PROFILES } from '../../data/mockData';
import { playHoloClick } from '../../utils/audioSynth';

interface DigitalTwinSceneProps {
  country: CountryCode;
  month: number;
  year?: number;
  scenario: ScenarioPreset;
  policyParams: PolicyParameters;
  workers: WorkerAgent[];
  firms: StructuralFirm[];
  selectedWorker: WorkerAgent | null;
  selectedFirm: StructuralFirm | null;
  onSelectWorker: (worker: WorkerAgent | null) => void;
  onSelectFirm: (firm: StructuralFirm | null) => void;
  deepZoomLevel: 'satellite' | 'isometric' | 'street';
  setDeepZoomLevel: (level: 'satellite' | 'isometric' | 'street') => void;
  isSimulatingTimeline: boolean;
  policyWaveTrigger: number;
  theme?: AppTheme;
}

interface OrganicNoduleMeta {
  r: number;
  angle: number;
  heightOffset: number;
  phase: number;
  speed: number;
  baseScale: number;
  color: THREE.Color;
}

export const DigitalTwinScene: React.FC<DigitalTwinSceneProps> = ({
  country,
  month,
  scenario,
  workers,
  firms,
  selectedWorker,
  selectedFirm,
  onSelectWorker,
  onSelectFirm,
  deepZoomLevel,
  isSimulatingTimeline,
  policyWaveTrigger,
  theme = 'dark',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const composerRef = useRef<EffectComposer | null>(null);
  const bloomPassRef = useRef<UnrealBloomPass | null>(null);
  const themeRef = useRef<AppTheme>(theme);

  // Dynamic simulation sync refs
  const monthRef = useRef(month);
  const workersRef = useRef(workers);
  const firmsRef = useRef(firms);

  // Mesh, scene group, and lighting refs
  const workersMeshRef = useRef<THREE.InstancedMesh | null>(null);
  const terrainMeshRef = useRef<THREE.Mesh | null>(null);
  const terrainGridRef = useRef<THREE.LineSegments | null>(null);
  const firmsGroupRef = useRef<THREE.Group | null>(null);
  const fiberLinesRef = useRef<THREE.LineSegments | null>(null);
  const waveRingRef = useRef<THREE.Mesh | null>(null);
  const shockwaveRingsRef = useRef<THREE.Mesh[]>([]);

  const overheadSunLightRef = useRef<THREE.DirectionalLight | null>(null);
  const ambientLightRef = useRef<THREE.AmbientLight | null>(null);
  const keyLightRef = useRef<THREE.DirectionalLight | null>(null);
  const fillLightRef = useRef<THREE.DirectionalLight | null>(null);
  const indigoLightRef = useRef<THREE.DirectionalLight | null>(null);
  const plinthMeshRef = useRef<THREE.Mesh | null>(null);
  const plinthEdgesRef = useRef<THREE.LineSegments | null>(null);
  const floorGridRef = useRef<THREE.GridHelper | null>(null);

  useEffect(() => {
    themeRef.current = theme;
    const scene = sceneRef.current;
    const bloomPass = bloomPassRef.current;
    const renderer = rendererRef.current;
    if (!scene) return;

    if (theme === 'light') {
      // 1. Fondo y Topografía: gris muy suave (#f8fafc) estricto
      scene.background = new THREE.Color(0xf8fafc);
      scene.fog = new THREE.FogExp2(0xf8fafc, 0.01);

      // 2. Apagar el Neón (Post-Processing): desactiva por completo el efecto Bloom
      if (bloomPass) {
        bloomPass.enabled = false;
        bloomPass.strength = 0.0;
      }
      if (renderer) {
        renderer.toneMappingExposure = 1.0;
      }

      // 3. Iluminación: DirectionalLight cenital fuerte para generar sombreado y devolver volumen
      if (overheadSunLightRef.current) {
        overheadSunLightRef.current.intensity = 3.6;
      }
      if (ambientLightRef.current) {
        ambientLightRef.current.color.set(0xffffff);
        ambientLightRef.current.intensity = 1.5;
      }
      if (keyLightRef.current) {
        keyLightRef.current.color.set(0x38bdf8);
        keyLightRef.current.intensity = 0.6;
      }
      if (fillLightRef.current) {
        fillLightRef.current.color.set(0xe2e8f0);
        fillLightRef.current.intensity = 0.5;
      }
      if (indigoLightRef.current) {
        indigoLightRef.current.intensity = 0.0;
      }

      // 4. Base Topografía y Wireframe: base clara y líneas wireframe en gris carbón (#334155)
      if (terrainMeshRef.current) {
        terrainMeshRef.current.material = new THREE.MeshStandardMaterial({
          color: 0xf1f5f9,
          roughness: 0.65,
          metalness: 0.08,
          flatShading: false,
        });
      }
      if (terrainGridRef.current) {
        terrainGridRef.current.material = new THREE.LineBasicMaterial({
          color: 0x334155, // Gris carbón estricto para destacar contra #f8fafc
          transparent: true,
          opacity: 0.75,
          blending: THREE.NormalBlending,
        });
      }

      // 5. Partículas de Trabajadores (Boids): MeshStandardMaterial (plástico mate/cristal sólido)
      if (workersMeshRef.current) {
        workersMeshRef.current.material = new THREE.MeshStandardMaterial({
          roughness: 0.38,
          metalness: 0.18,
          transparent: false,
          opacity: 1.0,
        });
      }

      // 6. Líneas de fibra óptica formales: azul cobalto profundo con NormalBlending
      if (fiberLinesRef.current) {
        fiberLinesRef.current.material = new THREE.LineBasicMaterial({
          color: 0x1d4ed8,
          transparent: true,
          opacity: 0.85,
          blending: THREE.NormalBlending,
        });
      }

      // 7. Zócalo / Pedestal y cuadrícula
      if (plinthMeshRef.current) {
        plinthMeshRef.current.material = new THREE.MeshStandardMaterial({
          color: 0xe2e8f0,
          roughness: 0.6,
          metalness: 0.1,
        });
      }
      if (plinthEdgesRef.current) {
        plinthEdgesRef.current.material = new THREE.LineBasicMaterial({
          color: 0x64748b,
          transparent: true,
          opacity: 0.5,
        });
      }
      if (floorGridRef.current) {
        floorGridRef.current.material = new THREE.LineBasicMaterial({
          color: 0xcbd5e1,
          transparent: true,
          opacity: 0.6,
        });
      }

      if (waveRingRef.current) {
        waveRingRef.current.material = new THREE.MeshBasicMaterial({
          color: 0x1d4ed8,
          transparent: true,
          opacity: 0,
          side: THREE.DoubleSide,
          blending: THREE.NormalBlending,
        });
      }
    } else {
      // MODO OSCURO (Obsidian / Neon Bloom)
      scene.background = new THREE.Color(0x04060b);
      scene.fog = new THREE.FogExp2(0x04060b, 0.018);

      if (bloomPass) {
        bloomPass.enabled = true;
        bloomPass.strength = 1.8;
        bloomPass.threshold = 0.18;
      }
      if (renderer) {
        renderer.toneMappingExposure = 1.25;
      }

      if (overheadSunLightRef.current) {
        overheadSunLightRef.current.intensity = 0.0;
      }
      if (ambientLightRef.current) {
        ambientLightRef.current.color.set(0x08101e);
        ambientLightRef.current.intensity = 1.8;
      }
      if (keyLightRef.current) {
        keyLightRef.current.color.set(0x00f0ff);
        keyLightRef.current.intensity = 2.2;
      }
      if (fillLightRef.current) {
        fillLightRef.current.color.set(0xf59e0b);
        fillLightRef.current.intensity = 1.3;
      }
      if (indigoLightRef.current) {
        indigoLightRef.current.color.set(0x1e3a8a);
        indigoLightRef.current.intensity = 1.6;
      }

      if (terrainMeshRef.current) {
        terrainMeshRef.current.material = new THREE.MeshPhysicalMaterial({
          color: 0x040813,
          roughness: 0.28,
          metalness: 0.7,
          clearcoat: 0.5,
          clearcoatRoughness: 0.18,
          flatShading: false,
        });
      }
      if (terrainGridRef.current) {
        terrainGridRef.current.material = new THREE.LineBasicMaterial({
          vertexColors: true,
          transparent: true,
          opacity: 0.35,
          blending: THREE.AdditiveBlending,
        });
      }

      if (workersMeshRef.current) {
        workersMeshRef.current.material = new THREE.MeshBasicMaterial({
          color: 0xffffff,
          transparent: true,
          opacity: 0.95,
        });
      }

      if (fiberLinesRef.current) {
        fiberLinesRef.current.material = new THREE.LineBasicMaterial({
          color: 0x00f0ff,
          transparent: true,
          opacity: 0.75,
          blending: THREE.AdditiveBlending,
        });
      }

      if (plinthMeshRef.current) {
        plinthMeshRef.current.material = new THREE.MeshStandardMaterial({
          color: 0x020409,
          roughness: 0.2,
          metalness: 0.8,
        });
      }
      if (plinthEdgesRef.current) {
        plinthEdgesRef.current.material = new THREE.LineBasicMaterial({
          color: 0x00e5ff,
          transparent: true,
          opacity: 0.45,
        });
      }
      if (floorGridRef.current) {
        floorGridRef.current.material = new THREE.LineBasicMaterial({
          color: 0x00f0ff,
          transparent: true,
          opacity: 0.35,
        });
      }

      if (waveRingRef.current) {
        waveRingRef.current.material = new THREE.MeshBasicMaterial({
          color: 0x00f0ff,
          transparent: true,
          opacity: 0,
          side: THREE.DoubleSide,
          blending: THREE.AdditiveBlending,
        });
      }
    }
  }, [theme]);

  useEffect(() => {
    monthRef.current = month;
  }, [month]);

  useEffect(() => {
    workersRef.current = workers;
  }, [workers]);

  useEffect(() => {
    firmsRef.current = firms;
  }, [firms]);

  // Interaction refs
  const isDraggingRef = useRef(false);
  const prevMousePos = useRef({ x: 0, y: 0 });
  const totalDragDist = useRef(0);
  const cameraAngle = useRef({ theta: Math.PI / 4, phi: Math.PI / 3, distance: 34 });
  const targetLookAt = useRef(new THREE.Vector3(0, 1.5, 0));
  const currentLookAt = useRef(new THREE.Vector3(0, 1.5, 0));

  // Current country terrain elevation formula
  const terrainFunc = (x: number, z: number, countryCode: CountryCode) => {
    const prof = COUNTRY_PROFILES[countryCode].terrainProfile;
    // Peaks near formal anchor hubs
    const dFormal1 = Math.hypot(x - (-8), z - (-6));
    const dFormal2 = Math.hypot(x - 7, z - (-7));
    const dFormal3 = Math.hypot(x - 0, z - (-10));
    
    // Formal plateau elevation
    const formalHeight = (
      Math.exp(-dFormal1 * 0.28) * 4.8 +
      Math.exp(-dFormal2 * 0.32) * 4.2 +
      Math.exp(-dFormal3 * 0.25) * 5.2
    );

    // Informal valley depressions
    const dValley = Math.hypot(x, z - 6);
    const valleyDepression = Math.sin(x * 0.18) * Math.cos(z * 0.18) * prof.valleyDepth - (dValley < 12 ? 1.5 : 0);

    // Macro landscape harmonic waves
    const waves = (Math.sin(x * 0.3 * prof.peakFrequency) + Math.cos(z * 0.3 * prof.peakFrequency)) * 0.6;

    return Math.max(-2.5, formalHeight + valleyDepression + waves);
  };

  // Helper to build solid obsidian terrain geometry with perimeter pedestal skirt
  const buildSolidTerrainGeometry = (countryCode: CountryCode) => {
    const size = 50;
    const segs = 80;
    const half = size / 2;
    const step = size / segs;
    const floorY = -3.8;

    const vertices: number[] = [];
    const indices: number[] = [];
    const colors: number[] = [];

    // 1. Top undulating surface grid
    for (let j = 0; j <= segs; j++) {
      const z = -half + j * step;
      for (let i = 0; i <= segs; i++) {
        const x = -half + i * step;
        const y = terrainFunc(x, z, countryCode);
        vertices.push(x, y, z);

        // Gradient color for terrain vertex shading
        if (y > 1.2) {
          // Plateau highlight
          colors.push(0.04, 0.12, 0.22);
        } else if (y < 0.0) {
          // Valley depression
          colors.push(0.05, 0.04, 0.03);
        } else {
          // Obsidian baseline
          colors.push(0.02, 0.03, 0.06);
        }
      }
    }

    // Top surface indices
    for (let j = 0; j < segs; j++) {
      for (let i = 0; i < segs; i++) {
        const a = j * (segs + 1) + i;
        const b = a + 1;
        const c = a + (segs + 1);
        const d = c + 1;
        indices.push(a, c, b);
        indices.push(b, c, d);
      }
    }

    // 2. Skirts around the 4 borders dropping to floorY
    const addSkirtEdge = (getCoords: (k: number) => { x: number; z: number }) => {
      for (let k = 0; k < segs; k++) {
        const p1 = getCoords(k);
        const p2 = getCoords(k + 1);
        const y1 = terrainFunc(p1.x, p1.z, countryCode);
        const y2 = terrainFunc(p2.x, p2.z, countryCode);

        const vIdx = vertices.length / 3;
        vertices.push(p1.x, y1, p1.z);
        vertices.push(p1.x, floorY, p1.z);
        vertices.push(p2.x, y2, p2.z);
        vertices.push(p2.x, floorY, p2.z);

        // Skirt dark color
        for (let c = 0; c < 4; c++) colors.push(0.015, 0.02, 0.04);

        indices.push(vIdx, vIdx + 1, vIdx + 2);
        indices.push(vIdx + 2, vIdx + 1, vIdx + 3);
      }
    };

    // North (z = -half)
    addSkirtEdge((k) => ({ x: -half + k * step, z: -half }));
    // South (z = half)
    addSkirtEdge((k) => ({ x: half - k * step, z: half }));
    // East (x = half)
    addSkirtEdge((k) => ({ x: half, z: -half + k * step }));
    // West (x = -half)
    addSkirtEdge((k) => ({ x: -half, z: half - k * step }));

    const geom = new THREE.BufferGeometry();
    geom.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geom.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    geom.setIndex(indices);
    geom.computeVertexNormals();
    return geom;
  };

  // Helper to build cybernetic overlay grid with dual-spectrum emission
  const buildCyberGridGeometry = (countryCode: CountryCode) => {
    const size = 50;
    const segs = 50;
    const half = size / 2;
    const step = size / segs;
    const positions: number[] = [];
    const colors: number[] = [];

    // Lines along X
    for (let j = 0; j <= segs; j += 2) {
      const z = -half + j * step;
      for (let i = 0; i < segs; i++) {
        const x1 = -half + i * step;
        const x2 = x1 + step;
        const y1 = terrainFunc(x1, z, countryCode) + 0.02;
        const y2 = terrainFunc(x2, z, countryCode) + 0.02;

        positions.push(x1, y1, z, x2, y2, z);

        // Color based on height and zone
        const avgY = (y1 + y2) / 2;
        if (avgY > 1.2) {
          // Glowing formal cyan
          colors.push(0.0, 0.94, 1.0, 0.0, 0.94, 1.0);
        } else if (avgY < 0.2) {
          // Warm informal amber
          colors.push(0.96, 0.62, 0.07, 0.96, 0.62, 0.07);
        } else {
          // Deep steel transition
          colors.push(0.1, 0.35, 0.6, 0.1, 0.35, 0.6);
        }
      }
    }

    // Lines along Z
    for (let i = 0; i <= segs; i += 2) {
      const x = -half + i * step;
      for (let j = 0; j < segs; j++) {
        const z1 = -half + j * step;
        const z2 = z1 + step;
        const y1 = terrainFunc(x, z1, countryCode) + 0.02;
        const y2 = terrainFunc(x, z2, countryCode) + 0.02;

        positions.push(x, y1, z1, x, y2, z2);

        const avgY = (y1 + y2) / 2;
        if (avgY > 1.2) {
          colors.push(0.0, 0.94, 1.0, 0.0, 0.94, 1.0);
        } else if (avgY < 0.2) {
          colors.push(0.96, 0.62, 0.07, 0.96, 0.62, 0.07);
        } else {
          colors.push(0.1, 0.35, 0.6, 0.1, 0.35, 0.6);
        }
      }
    }

    const geom = new THREE.BufferGeometry();
    geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geom.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    return geom;
  };

  // Re-generate Terrain geometry when country changes
  useEffect(() => {
    if (!terrainMeshRef.current || !terrainGridRef.current) return;

    const newSolidGeom = buildSolidTerrainGeometry(country);
    terrainMeshRef.current.geometry.dispose();
    terrainMeshRef.current.geometry = newSolidGeom;

    const newGridGeom = buildCyberGridGeometry(country);
    terrainGridRef.current.geometry.dispose();
    terrainGridRef.current.geometry = newGridGeom;

    cameraAngle.current.theta = Math.PI / 4;
  }, [country]);

  // Adjust camera distance for deepZoomLevel
  useEffect(() => {
    if (deepZoomLevel === 'satellite') {
      cameraAngle.current.distance = 52;
      targetLookAt.current.set(0, 0, 0);
    } else if (deepZoomLevel === 'isometric') {
      cameraAngle.current.distance = 32;
      targetLookAt.current.set(0, 2, 0);
    } else if (deepZoomLevel === 'street') {
      cameraAngle.current.distance = 14;
      if (selectedFirm) {
        targetLookAt.current.set(selectedFirm.x, 3, selectedFirm.z);
      } else if (selectedWorker) {
        targetLookAt.current.set(selectedWorker.x, 1, selectedWorker.z);
      } else {
        targetLookAt.current.set(-2, 1, 2);
      }
    }
  }, [deepZoomLevel, selectedFirm, selectedWorker]);

  // Trigger Policy Wave expansion
  useEffect(() => {
    if (!waveRingRef.current || policyWaveTrigger === 0) return;
    waveRingRef.current.scale.set(0.1, 0.1, 0.1);
    waveRingRef.current.visible = true;
    (waveRingRef.current.material as THREE.MeshBasicMaterial).opacity = 0.95;
  }, [policyWaveTrigger]);

  // Main Three.js setup, Postprocessing pipeline and Animation Loop
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // 1. Scene & Volumetric Fog
    const scene = new THREE.Scene();
    const isInitLight = theme === 'light';
    scene.background = new THREE.Color(isInitLight ? 0xf8fafc : 0x04060b);
    scene.fog = new THREE.FogExp2(isInitLight ? 0xf8fafc : 0x04060b, isInitLight ? 0.01 : 0.018);
    sceneRef.current = scene;

    // 2. Camera
    const camera = new THREE.PerspectiveCamera(40, container.clientWidth / container.clientHeight, 0.1, 1000);
    cameraRef.current = camera;

    // 3. WebGL Renderer with ACES Filmic Tone Mapping
    const renderer = new THREE.WebGLRenderer({ 
      antialias: true, 
      alpha: true, 
      powerPreference: 'high-performance' 
    });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = isInitLight ? 1.0 : 1.25;
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // 4. Post-Processing Pipeline (EffectComposer + UnrealBloomPass + OutputPass)
    const composer = new EffectComposer(renderer);
    const renderPass = new RenderPass(scene, camera);
    composer.addPass(renderPass);

    const bloomPass = new UnrealBloomPass(
      new THREE.Vector2(container.clientWidth, container.clientHeight),
      isInitLight ? 0.0 : 1.8, // In Light Mode: completely disabled
      0.65,
      isInitLight ? 0.95 : 0.18
    );
    if (isInitLight) {
      bloomPass.enabled = false;
    }
    composer.addPass(bloomPass);
    bloomPassRef.current = bloomPass;

    const outputPass = new OutputPass();
    composer.addPass(outputPass);
    composerRef.current = composer;

    // 5. Lighting: Strong overhead directional light for daylight volume + Sci-Fi accents
    const overheadSunLight = new THREE.DirectionalLight(0xffffff, isInitLight ? 3.6 : 0.0);
    overheadSunLight.position.set(12, 50, 15);
    scene.add(overheadSunLight);
    overheadSunLightRef.current = overheadSunLight;

    const ambientLight = new THREE.AmbientLight(
      isInitLight ? 0xffffff : 0x08101e, 
      isInitLight ? 1.5 : 1.8
    );
    scene.add(ambientLight);
    ambientLightRef.current = ambientLight;

    // Key Directional Light
    const keyLight = new THREE.DirectionalLight(
      isInitLight ? 0x38bdf8 : 0x00f0ff, 
      isInitLight ? 0.6 : 2.2
    );
    keyLight.position.set(24, 45, 20);
    scene.add(keyLight);
    keyLightRef.current = keyLight;

    // Fill Directional Light
    const fillLight = new THREE.DirectionalLight(
      isInitLight ? 0xe2e8f0 : 0xf59e0b, 
      isInitLight ? 0.5 : 1.3
    );
    fillLight.position.set(-20, 18, -25);
    scene.add(fillLight);
    fillLightRef.current = fillLight;

    // Deep Indigo Rim Light (Underglow, only in dark mode)
    const indigoLight = new THREE.DirectionalLight(0x1e3a8a, isInitLight ? 0.0 : 1.6);
    indigoLight.position.set(0, -15, 30);
    scene.add(indigoLight);
    indigoLightRef.current = indigoLight;

    // 6. Architectural Monolithic Pedestal Base Plinth
    const plinthGeom = new THREE.BoxGeometry(50.4, 0.4, 50.4);
    const plinthMat = new THREE.MeshStandardMaterial({
      color: isInitLight ? 0xe2e8f0 : 0x020409,
      roughness: isInitLight ? 0.6 : 0.2,
      metalness: isInitLight ? 0.1 : 0.8,
    });
    const plinthMesh = new THREE.Mesh(plinthGeom, plinthMat);
    plinthMesh.position.y = -3.95;
    scene.add(plinthMesh);
    plinthMeshRef.current = plinthMesh;

    // Plinth Cyan / Slate Laser Trim
    const plinthEdges = new THREE.LineSegments(
      new THREE.EdgesGeometry(plinthGeom),
      new THREE.LineBasicMaterial({ 
        color: isInitLight ? 0x64748b : 0x00e5ff, 
        transparent: true, 
        opacity: isInitLight ? 0.5 : 0.45 
      })
    );
    plinthEdges.position.y = -3.95;
    scene.add(plinthEdges);
    plinthEdgesRef.current = plinthEdges;

    // Sub-floor spatial coordinate grid
    const floorGrid = new THREE.GridHelper(
      70, 
      70, 
      isInitLight ? 0x94a3b8 : 0x00f0ff, 
      isInitLight ? 0xe2e8f0 : 0x091c30
    );
    floorGrid.position.y = -4.15;
    scene.add(floorGrid);
    floorGridRef.current = floorGrid;

    // 7. Base Topography Mesh
    const solidGeom = buildSolidTerrainGeometry(country);
    const solidMat = isInitLight
      ? new THREE.MeshStandardMaterial({
          color: 0xf1f5f9,
          roughness: 0.65,
          metalness: 0.08,
          flatShading: false,
        })
      : new THREE.MeshPhysicalMaterial({
          color: 0x040813,
          roughness: 0.28,
          metalness: 0.7,
          clearcoat: 0.5,
          clearcoatRoughness: 0.18,
          flatShading: false,
        });
    const terrainMesh = new THREE.Mesh(solidGeom, solidMat);
    scene.add(terrainMesh);
    terrainMeshRef.current = terrainMesh;

    // 8. Superimposed Topography Grid (Charcoal #334155 in Light Mode)
    const cyberGridGeom = buildCyberGridGeometry(country);
    const cyberGridMat = isInitLight
      ? new THREE.LineBasicMaterial({
          color: 0x334155, // Charcoal gray to stand out cleanly against #f8fafc
          transparent: true,
          opacity: 0.75,
          blending: THREE.NormalBlending,
        })
      : new THREE.LineBasicMaterial({
          vertexColors: true,
          transparent: true,
          opacity: 0.35,
          blending: THREE.AdditiveBlending,
        });
    const terrainGrid = new THREE.LineSegments(cyberGridGeom, cyberGridMat);
    scene.add(terrainGrid);
    terrainGridRef.current = terrainGrid;

    // 9. Policy Sweep Wave Ring
    const waveGeom = new THREE.RingGeometry(0.1, 0.9, 64);
    waveGeom.rotateX(-Math.PI / 2);
    const waveMat = new THREE.MeshBasicMaterial({
      color: isInitLight ? 0x1d4ed8 : 0x00f0ff,
      transparent: true,
      opacity: 0,
      side: THREE.DoubleSide,
      blending: isInitLight ? THREE.NormalBlending : THREE.AdditiveBlending,
    });
    const waveMesh = new THREE.Mesh(waveGeom, waveMat);
    waveMesh.position.y = 0.25;
    waveMesh.visible = false;
    scene.add(waveMesh);
    waveRingRef.current = waveMesh;

    // 10. Worker Agents Instanced Mesh (2,500 particles with MeshStandardMaterial in Light Mode)
    const workerGeom = new THREE.SphereGeometry(0.18, 10, 8);
    const workerMat = isInitLight
      ? new THREE.MeshStandardMaterial({
          roughness: 0.38,
          metalness: 0.18,
          transparent: false,
          opacity: 1.0,
        })
      : new THREE.MeshBasicMaterial({
          color: 0xffffff,
          transparent: true,
          opacity: 0.95,
        });
    const instancedWorkers = new THREE.InstancedMesh(workerGeom, workerMat, workers.length);
    instancedWorkers.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    scene.add(instancedWorkers);
    workersMeshRef.current = instancedWorkers;

    // 11. Structural Firms Group (Formal Crystal Towers & Informal Organic Mycelial Swarms)
    const firmsGroup = new THREE.Group();
    scene.add(firmsGroup);
    firmsGroupRef.current = firmsGroup;

    // 12. Fiber Optical Laser Lines (Formal connectivity: cobalt in Light Mode)
    const maxLines = 450;
    const fiberGeom = new THREE.BufferGeometry();
    const fiberPositions = new Float32Array(maxLines * 6);
    fiberGeom.setAttribute('position', new THREE.BufferAttribute(fiberPositions, 3));
    const fiberMat = isInitLight
      ? new THREE.LineBasicMaterial({
          color: 0x1d4ed8,
          transparent: true,
          opacity: 0.85,
          blending: THREE.NormalBlending,
        })
      : new THREE.LineBasicMaterial({
          color: 0x00f0ff,
          transparent: true,
          opacity: 0.75,
          blending: THREE.AdditiveBlending,
        });
    const fiberLines = new THREE.LineSegments(fiberGeom, fiberMat);
    scene.add(fiberLines);
    fiberLinesRef.current = fiberLines;

    // Resize Observer for dynamic canvas adaptation
    const resizeObserver = new ResizeObserver(() => {
      if (!container || !renderer || !camera || !composer) return;
      const width = container.clientWidth;
      const height = container.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
      composer.setSize(width, height);
      bloomPass.resolution.set(width, height);
    });
    resizeObserver.observe(container);

    // Camera Orbit Mouse / Touch Handlers
    const onMouseDown = (e: MouseEvent) => {
      isDraggingRef.current = true;
      prevMousePos.current = { x: e.clientX, y: e.clientY };
      totalDragDist.current = 0;
    };

    const onMouseMove = (e: MouseEvent) => {
      if (!isDraggingRef.current) return;
      const dx = e.clientX - prevMousePos.current.x;
      const dy = e.clientY - prevMousePos.current.y;
      prevMousePos.current = { x: e.clientX, y: e.clientY };
      totalDragDist.current += Math.hypot(dx, dy);

      cameraAngle.current.theta -= dx * 0.007;
      cameraAngle.current.phi = Math.max(0.18, Math.min(Math.PI / 2 - 0.05, cameraAngle.current.phi - dy * 0.007));
    };

    const onMouseUp = () => {
      isDraggingRef.current = false;
    };

    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      cameraAngle.current.distance = Math.max(8, Math.min(70, cameraAngle.current.distance + e.deltaY * 0.03));
    };

    const domElement = renderer.domElement;
    domElement.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    domElement.addEventListener('wheel', onWheel, { passive: false });

    // Raycaster for Entity Selection
    const raycaster = new THREE.Raycaster();
    const mouseCoord = new THREE.Vector2();

    const handleClick = (e: MouseEvent) => {
      // Suppress click if user was orbiting camera
      if (totalDragDist.current > 5) return;

      const rect = domElement.getBoundingClientRect();
      mouseCoord.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouseCoord.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouseCoord, camera);

      // Check firm intersections
      if (firmsGroupRef.current) {
        const firmIntersects = raycaster.intersectObjects(firmsGroupRef.current.children, true);
        if (firmIntersects.length > 0) {
          // Look for firmId in object hierarchy
          let hitObj: THREE.Object3D | null = firmIntersects[0].object;
          let firmId: string | undefined;
          while (hitObj && !firmId) {
            firmId = hitObj.userData?.firmId;
            hitObj = hitObj.parent;
          }

          if (firmId) {
            const foundFirm = firms.find((f) => f.id === firmId);
            if (foundFirm) {
              playHoloClick(1100);
              onSelectFirm(foundFirm);
              onSelectWorker(null);
              return;
            }
          }
        }
      }

      // Check nearest worker click approximation
      let nearestWorker: WorkerAgent | null = null;
      let minDistance = 1.4;

      const ray = raycaster.ray;
      for (const w of workers) {
        const wPos = new THREE.Vector3(w.x, w.y, w.z);
        const dist = ray.distanceToPoint(wPos);
        if (dist < minDistance) {
          minDistance = dist;
          nearestWorker = w;
        }
      }

      if (nearestWorker) {
        playHoloClick(950);
        onSelectWorker(nearestWorker);
        onSelectFirm(null);
      } else {
        onSelectWorker(null);
        onSelectFirm(null);
      }
    };

    domElement.addEventListener('click', handleClick);

    // Animation Loop
    let animationFrameId: number;
    const clock = new THREE.Clock();
    const dummy = new THREE.Object3D();
    const colorDummy = new THREE.Color();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();
      const currentMonth = monthRef.current;
      const currentWorkers = workersRef.current;
      const currentFirms = firmsRef.current;
      const isLightMode = themeRef.current === 'light';

      // Color templates: in Light Mode use deep, saturated, high-contrast tones against #f8fafc:
      // Formal Sector: Deep Cobalt (#1d4ed8) to Navy Blue (#1e3a8a)
      // Informal Sector: Terracotta (#c2410c) to Dark Rust Red (#9a3412)
      const colorFormalCobalt = new THREE.Color(0x1d4ed8);
      const colorFormalNavy = new THREE.Color(0x1e3a8a);
      const colorInformalTerracotta = new THREE.Color(0xc2410c);
      const colorInformalRust = new THREE.Color(0x9a3412);
      const colorUnemp = isLightMode ? new THREE.Color(0x475569) : new THREE.Color(0x64748b);
      const colorWhite = isLightMode ? new THREE.Color(0x0f172a) : new THREE.Color(0xffffff);

      const colorAmber = new THREE.Color(0xf59e0b);
      const colorVermilion = new THREE.Color(0xef4444);
      const colorNeonCyan = new THREE.Color(0x00f0ff);
      const colorDeepSky = new THREE.Color(0x0284c7);

      // Smooth Camera tracking
      currentLookAt.current.lerp(targetLookAt.current, 0.06);

      const targetX = currentLookAt.current.x + cameraAngle.current.distance * Math.sin(cameraAngle.current.phi) * Math.sin(cameraAngle.current.theta);
      const targetY = currentLookAt.current.y + cameraAngle.current.distance * Math.cos(cameraAngle.current.phi);
      const targetZ = currentLookAt.current.z + cameraAngle.current.distance * Math.sin(cameraAngle.current.phi) * Math.cos(cameraAngle.current.theta);

      camera.position.x += (targetX - camera.position.x) * 0.08;
      camera.position.y += (targetY - camera.position.y) * 0.08;
      camera.position.z += (targetZ - camera.position.z) * 0.08;
      camera.lookAt(currentLookAt.current);

      // Policy sweep wave expansion
      if (waveMesh.visible) {
        const currentScale = waveMesh.scale.x;
        if (currentScale < 35) {
          waveMesh.scale.addScalar(0.55);
          (waveMat as THREE.MeshBasicMaterial).opacity = Math.max(0, 0.95 - currentScale / 35);
        } else {
          waveMesh.visible = false;
        }
      }

      // Update Workers positions & InstancedMesh (Continuous month-by-month evolution with Lerp)
      if (instancedWorkers && currentWorkers.length > 0) {
        const lineAttr = fiberLines.geometry.attributes.position;
        const lineArr = lineAttr.array as Float32Array;
        let lineIndex = 0;

        const activeFormalFirms = currentFirms.filter((f) => f.type === 'formal' || f.isFormalizedScenario);

        for (let i = 0; i < currentWorkers.length; i++) {
          const w = currentWorkers[i];

          // 1. Determine target formalization progress based on continuous month
          const formalMonth = w.formalizationMonth ?? 120;
          let targetProgress = 0.0;

          if (w.sector === 'unemployed') {
            targetProgress = 0.0;
          } else if (formalMonth === 0) {
            targetProgress = 1.0;
          } else if (currentMonth >= formalMonth) {
            targetProgress = 1.0;
          } else if (currentMonth >= formalMonth - 10) {
            // Smooth 10-month transition window
            targetProgress = (currentMonth - (formalMonth - 10)) / 10;
          } else {
            targetProgress = 0.0;
          }

          // 2. Smoothly interpolate transition progress over animation frames (Lerp)
          if (w.currentProgress === undefined) {
            w.currentProgress = targetProgress;
          } else {
            w.currentProgress = THREE.MathUtils.lerp(w.currentProgress, targetProgress, 0.08);
          }
          const p = w.currentProgress; // 0 = fully informal, 1 = fully formal

          // 3. Informal Brownian Motion Simulation (in valleys)
          if (w.informalX === undefined) w.informalX = w.x;
          if (w.informalZ === undefined) w.informalZ = w.z;

          w.informalX += w.vx * (isSimulatingTimeline ? 2.2 : 1);
          w.informalZ += w.vz * (isSimulatingTimeline ? 2.2 : 1);

          if (Math.abs(w.informalX) > 22) w.vx *= -1;
          if (Math.abs(w.informalZ) > 22) w.vz *= -1;

          w.vx += (Math.random() - 0.5) * 0.008;
          w.vz += (Math.random() - 0.5) * 0.008;
          w.vx = Math.max(-0.06, Math.min(0.06, w.vx));
          w.vz = Math.max(-0.06, Math.min(0.06, w.vz));

          const groundYInf = terrainFunc(w.informalX, w.informalZ, country);
          const yInf = groundYInf + 0.25 + Math.sin(elapsed * 2 + i) * 0.1;

          // 4. Formal Orbital Motion Simulation (around host crystal prism)
          const hostFirm = currentFirms.find((f) => f.id === w.firmId) || 
                           activeFormalFirms[i % Math.max(1, activeFormalFirms.length)] || 
                           currentFirms[0];

          w.orbitAngle += (w.orbitSpeed || 0.015) * (isSimulatingTimeline ? 2.5 : 1);
          const radius = w.orbitRadius || 2.4;
          const xForm = hostFirm.x + Math.cos(w.orbitAngle) * radius;
          const zForm = hostFirm.z + Math.sin(w.orbitAngle) * radius;
          const groundYForm = terrainFunc(xForm, zForm, country);
          const yForm = Math.max(groundYForm + 0.4, groundYForm + Math.sin(w.orbitAngle * 2 + i) * 0.3 + 0.5);

          // 5. Blend physical coordinates and colors using Lerp
          if (w.sector === 'unemployed') {
            w.x = w.informalX;
            w.z = w.informalZ;
            w.y = groundYInf + 0.15;
            colorDummy.copy(colorUnemp);
          } else {
            // Dynamic physical migration between valley swarm and crystal orbit
            w.x = THREE.MathUtils.lerp(w.informalX, xForm, p);
            w.z = THREE.MathUtils.lerp(w.informalZ, zForm, p);
            w.y = THREE.MathUtils.lerp(yInf, yForm, p);

            // Dynamic color migration:
            // Light Mode: Terracotta / Rust -> Deep Cobalt / Navy Blue
            // Dark Mode: Amber / Vermilion -> Neon Cyan / Deep Sky
            const baseWarm = isLightMode
              ? (w.incomeUSDDay > 12 ? colorInformalTerracotta : colorInformalRust)
              : (w.incomeUSDDay > 12 ? colorAmber : colorVermilion);
            const baseCool = isLightMode
              ? (w.incomeUSDDay > 25 ? colorFormalCobalt : colorFormalNavy)
              : (w.incomeUSDDay > 25 ? colorNeonCyan : colorDeepSky);
            colorDummy.copy(baseWarm).lerp(baseCool, p);

            // Connect laser fiber line when particle formalizes (p > 0.45)
            if (p > 0.45 && lineIndex < maxLines * 6 && hostFirm) {
              lineArr[lineIndex++] = hostFirm.x;
              lineArr[lineIndex++] = (hostFirm.height || 5) * 0.6 * Math.max(0.2, p) + 0.5;
              lineArr[lineIndex++] = hostFirm.z;
              lineArr[lineIndex++] = w.x;
              lineArr[lineIndex++] = w.y;
              lineArr[lineIndex++] = w.z;
            }
          }

          if (selectedWorker && selectedWorker.id === w.id) {
            colorDummy.copy(colorWhite);
          }

          const scale = (0.7 + (w.humanCapital / 100) * 0.9) * (selectedWorker?.id === w.id ? 1.9 : 1);

          dummy.position.set(w.x, w.y, w.z);
          dummy.scale.set(scale, scale, scale);
          dummy.updateMatrix();

          instancedWorkers.setMatrixAt(i, dummy.matrix);
          instancedWorkers.setColorAt(i, colorDummy);
        }

        instancedWorkers.instanceMatrix.needsUpdate = true;
        if (instancedWorkers.instanceColor) {
          instancedWorkers.instanceColor.needsUpdate = true;
        }
        lineAttr.needsUpdate = true;
      }

      // Update Structural Firms: Dynamic Physical Growth from Ground (Scale.Y: 0 to 1)
      if (firmsGroupRef.current) {
        firmsGroupRef.current.children.forEach((child) => {
          const firmId = child.userData?.firmId;
          const firmData = currentFirms.find((f) => f.id === firmId);

          if (firmData && (firmData.type === 'formal' || firmData.isFormalizedScenario)) {
            const emergence = firmData.emergenceMonth ?? 0;
            const growthSpan = firmData.growthSpanMonths ?? 10;

            let targetScaleY = 1.0;
            if (currentMonth < emergence) {
              targetScaleY = 0.001; // dormant beneath ground
            } else if (currentMonth < emergence + growthSpan) {
              targetScaleY = (currentMonth - emergence) / growthSpan; // physical growth interpolation
            } else {
              targetScaleY = 1.0; // fully mature crystal tower
            }

            if (child.userData.currentScaleY === undefined) {
              child.userData.currentScaleY = targetScaleY;
            } else {
              child.userData.currentScaleY = THREE.MathUtils.lerp(
                child.userData.currentScaleY,
                targetScaleY,
                0.08
              );
            }

            const sY = Math.max(0.001, child.userData.currentScaleY);
            // Animate scale in Y from ground up, and slight horizontal crystallization
            child.scale.set(Math.min(1.0, 0.15 + sY * 0.85), sY, Math.min(1.0, 0.15 + sY * 0.85));
            child.visible = sY > 0.01;
          }

          // 1. Formal Neon Core pulse
          if (child.userData?.coreMesh) {
            const cMesh = child.userData.coreMesh as THREE.Mesh;
            const pScale = 0.92 + Math.sin(elapsed * 3.2 + child.position.x) * 0.08;
            cMesh.scale.set(pScale, 1, pScale);
          }

          // 2. Formal Orbital Rings rotation
          if (child.userData?.ringMesh) {
            const rMesh = child.userData.ringMesh as THREE.Mesh;
            rMesh.rotation.z = elapsed * 0.8;
          }

          // 3. Formal Core Point Light pulse
          if (child.userData?.formalLight) {
            const fLight = child.userData.formalLight as THREE.PointLight;
            fLight.intensity = 3.5 + Math.sin(elapsed * 3.5 + child.position.z) * 0.8;
          }

          // 4. Informal Organic Particle Swarm update (Perlin-style 3D harmonic noise drift)
          if (child.userData?.clusterMesh && child.userData?.nodulesData) {
            const cMesh = child.userData.clusterMesh as THREE.InstancedMesh;
            const nodules = child.userData.nodulesData as OrganicNoduleMeta[];

            for (let k = 0; k < nodules.length; k++) {
              const nod = nodules[k];

              // Turbulent noise drift
              const noiseX = Math.sin(elapsed * nod.speed + nod.phase) * 0.35 + Math.cos(elapsed * 1.5 + nod.phase * 2) * 0.15;
              const noiseZ = Math.cos(elapsed * nod.speed + nod.phase) * 0.35 + Math.sin(elapsed * 1.7 + nod.phase * 1.5) * 0.15;
              const noiseY = Math.sin(elapsed * 2.4 + nod.phase * 2.5) * 0.22;

              const px = nod.r * Math.cos(nod.angle) + noiseX;
              const pz = nod.r * Math.sin(nod.angle) + noiseZ;
              const py = nod.heightOffset + noiseY;

              const pScale = nod.baseScale * (0.9 + Math.sin(elapsed * 3.0 + nod.phase) * 0.3);

              dummy.position.set(px, py, pz);
              dummy.scale.setScalar(pScale);
              dummy.updateMatrix();

              cMesh.setMatrixAt(k, dummy.matrix);
            }
            cMesh.instanceMatrix.needsUpdate = true;
          }

          // 5. Informal Warm Hearth Light pulse
          if (child.userData?.hearthLight) {
            const hLight = child.userData.hearthLight as THREE.PointLight;
            hLight.intensity = 2.4 + Math.sin(elapsed * 2.2 + child.position.x) * 0.8;
          }
        });
      }

      // Animate shockwave rings (Scenario E Tech Shock)
      shockwaveRingsRef.current.forEach((ring) => {
        if (ring.visible) {
          ring.scale.addScalar(0.35);
          const mat = ring.material as THREE.MeshBasicMaterial;
          mat.opacity = Math.max(0, mat.opacity - 0.015);
          if (mat.opacity <= 0.01) {
            ring.visible = false;
          }
        }
      });

      // Post-processed Render
      composer.render();
    };

    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      resizeObserver.disconnect();
      domElement.removeEventListener('mousedown', onMouseDown);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      domElement.removeEventListener('wheel', onWheel);
      domElement.removeEventListener('click', handleClick);
      composer.dispose();
      renderer.dispose();
      if (renderer.domElement.parentElement) {
        renderer.domElement.parentElement.removeChild(renderer.domElement);
      }
    };
  }, []);

  // Update Firms 3D entities when firms array, theme, or scenario changes
  useEffect(() => {
    const firmsGroup = firmsGroupRef.current;
    if (!firmsGroup) return;

    const isLightMode = theme === 'light';

    // Clear old firm children
    while (firmsGroup.children.length > 0) {
      const obj = firmsGroup.children[0];
      firmsGroup.remove(obj);
    }
    shockwaveRingsRef.current = [];

    firms.forEach((firm) => {
      const firmPivot = new THREE.Group();
      firmPivot.position.set(firm.x, terrainFunc(firm.x, firm.z, country), firm.z);
      firmPivot.userData = { firmId: firm.id };

      if (firm.type === 'formal' || firm.isFormalizedScenario) {
        // ==========================================
        // 1. FORMAL SECTOR: CRYSTAL PRISM / STRUCTURAL TOWER
        // ==========================================
        const height = firm.height || 5.2;
        const radiusTop = 1.6;
        const radiusBottom = 1.85;

        // Outer Hexagonal Crystal Column
        const hexGeom = new THREE.CylinderGeometry(radiusTop, radiusBottom, height, 6);
        hexGeom.translate(0, height / 2, 0);

        // Light mode: MeshStandardMaterial (matte solid prism in cobalt/navy blue)
        // Dark mode: MeshPhysicalMaterial (translucent holographic crystal glass)
        const hexMat = isLightMode
          ? new THREE.MeshStandardMaterial({
              color: 0x1e3a8a, // Deep navy/cobalt blue
              roughness: 0.28,
              metalness: 0.22,
              transparent: false,
              opacity: 1.0,
            })
          : new THREE.MeshPhysicalMaterial({
              color: 0x00e5ff,
              transparent: true,
              opacity: 1.0,
              transmission: 0.93,
              roughness: 0.05,
              metalness: 0.12,
              ior: 1.55,
              thickness: 2.6,
              specularIntensity: 1.0,
              specularColor: new THREE.Color(0x00ffff),
              attenuationColor: new THREE.Color(0x004488),
              attenuationDistance: 4.0,
            });

        const hexMesh = new THREE.Mesh(hexGeom, hexMat);
        hexMesh.userData = { firmId: firm.id };
        firmPivot.add(hexMesh);

        // Chamfer Edge Lines: Dark slate/navy in Light Mode, glowing cyan in Dark Mode
        const wireGeom = new THREE.WireframeGeometry(hexGeom);
        const wireMat = new THREE.LineBasicMaterial({
          color: isLightMode
            ? (selectedFirm?.id === firm.id ? 0x020617 : 0x1d4ed8)
            : (selectedFirm?.id === firm.id ? 0xffffff : 0x00f0ff),
          transparent: true,
          opacity: isLightMode ? 0.9 : 0.85,
          blending: isLightMode ? THREE.NormalBlending : THREE.AdditiveBlending,
        });
        const wireLines = new THREE.LineSegments(wireGeom, wireMat);
        firmPivot.add(wireLines);

        // Interior Core Column
        const coreGeom = new THREE.CylinderGeometry(0.7, 0.85, height * 0.88, 6);
        coreGeom.translate(0, height / 2, 0);
        const coreMat = isLightMode
          ? new THREE.MeshStandardMaterial({
              color: 0x1d4ed8, // Pure cobalt blue
              roughness: 0.35,
              metalness: 0.2,
            })
          : new THREE.MeshBasicMaterial({
              color: 0x00f0ff,
              transparent: true,
              opacity: 0.9,
              blending: THREE.AdditiveBlending,
            });
        const coreMesh = new THREE.Mesh(coreGeom, coreMat);
        firmPivot.add(coreMesh);
        firmPivot.userData.coreMesh = coreMesh;

        // Active Point Light inside the tower
        const formalPointLight = new THREE.PointLight(
          isLightMode ? 0x1d4ed8 : 0x00f0ff, 
          isLightMode ? 1.4 : 3.8, 
          isLightMode ? 10 : 14
        );
        formalPointLight.position.set(0, height * 0.5, 0);
        firmPivot.add(formalPointLight);
        firmPivot.userData.formalLight = formalPointLight;

        // Floating Rotating Collar Ring
        const ringGeom = new THREE.TorusGeometry(2.3, 0.04, 16, 48);
        ringGeom.rotateX(Math.PI / 2);
        const ringMat = isLightMode
          ? new THREE.MeshStandardMaterial({
              color: 0x2563eb,
              roughness: 0.3,
              metalness: 0.2,
            })
          : new THREE.MeshBasicMaterial({
              color: 0x00e5ff,
              transparent: true,
              opacity: 0.75,
              blending: THREE.AdditiveBlending,
            });
        const ringMesh = new THREE.Mesh(ringGeom, ringMat);
        ringMesh.position.y = height * 0.7;
        firmPivot.add(ringMesh);
        firmPivot.userData.ringMesh = ringMesh;

        // Shockwave ring for Scenario E (Automation Shock)
        const shockGeom = new THREE.RingGeometry(0.2, 0.7, 32);
        shockGeom.rotateX(-Math.PI / 2);
        const shockMat = new THREE.MeshBasicMaterial({
          color: 0xef4444,
          transparent: true,
          opacity: 0,
          side: THREE.DoubleSide,
          blending: isLightMode ? THREE.NormalBlending : THREE.AdditiveBlending,
        });
        const shockRing = new THREE.Mesh(shockGeom, shockMat);
        shockRing.position.y = 0.3;
        shockRing.visible = false;
        firmPivot.add(shockRing);
        shockwaveRingsRef.current.push(shockRing);

        if (scenario === 'SCENARIO_E_AUTOMATION_SHOCK' && firm.id === 'firm-f-01') {
          shockRing.visible = true;
          shockRing.scale.set(1, 1, 1);
          shockMat.opacity = 0.95;
        }
      } else {
        // ==========================================
        // 2. INFORMAL SECTOR: SWARM & MYCELIAL NODULES
        // ==========================================
        const PARTICLE_COUNT = 110;
        const clusterGeom = new THREE.DodecahedronGeometry(0.18, 0);

        // Light mode: MeshStandardMaterial (matte solid nodules)
        // Dark mode: MeshBasicMaterial (bioluminescent additive embers)
        const clusterMat = isLightMode
          ? new THREE.MeshStandardMaterial({
              vertexColors: true,
              roughness: 0.45,
              metalness: 0.1,
            })
          : new THREE.MeshBasicMaterial({
              vertexColors: true,
              blending: THREE.AdditiveBlending,
            });

        const instancedCluster = new THREE.InstancedMesh(clusterGeom, clusterMat, PARTICLE_COUNT);
        instancedCluster.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
        instancedCluster.userData = { firmId: firm.id };

        const nodulesData: OrganicNoduleMeta[] = [];
        // Paleta informal en Modo Claro: Terracota y Rojo Óxido profundos (#c2410c, #9a3412, #7c2d12)
        const warmPalette = isLightMode
          ? [
              new THREE.Color(0xc2410c), // terracotta
              new THREE.Color(0x9a3412), // dark rust red
              new THREE.Color(0x7c2d12), // deep terracotta earth
              new THREE.Color(0xb45309), // burnt amber
              new THREE.Color(0x854d0e), // dark ochre
            ]
          : [
              new THREE.Color(0xf59e0b), // amber
              new THREE.Color(0xf97316), // fiery orange
              new THREE.Color(0xef4444), // crimson
              new THREE.Color(0xfacc15), // golden spark
            ];

        const clusterDummy = new THREE.Object3D();

        for (let k = 0; k < PARTICLE_COUNT; k++) {
          // Asymmetric spiral & noise distribution
          const r = 0.6 + Math.pow(Math.random(), 0.7) * 2.4;
          const angle = Math.random() * Math.PI * 2;
          const heightOffset = 0.2 + Math.random() * 1.6 * (1 - r / 3.2);
          const phase = Math.random() * Math.PI * 2;
          const speed = 1.2 + Math.random() * 2.0;
          const baseScale = 0.7 + Math.random() * 0.9;
          const color = warmPalette[Math.floor(Math.random() * warmPalette.length)].clone();

          nodulesData.push({ r, angle, heightOffset, phase, speed, baseScale, color });

          clusterDummy.position.set(r * Math.cos(angle), heightOffset, r * Math.sin(angle));
          clusterDummy.scale.setScalar(baseScale);
          clusterDummy.updateMatrix();

          instancedCluster.setMatrixAt(k, clusterDummy.matrix);
          instancedCluster.setColorAt(k, color);
        }

        instancedCluster.instanceMatrix.needsUpdate = true;
        if (instancedCluster.instanceColor) instancedCluster.instanceColor.needsUpdate = true;

        firmPivot.add(instancedCluster);
        firmPivot.userData.clusterMesh = instancedCluster;
        firmPivot.userData.nodulesData = nodulesData;

        // Mycelium Root Tendrils (Creeping along terrain)
        const tendrilLines = 28;
        const tendrilPositions: number[] = [];
        for (let t = 0; t < tendrilLines; t++) {
          const rootAngle = (t / tendrilLines) * Math.PI * 2 + (Math.random() - 0.5) * 0.3;
          let curX = 0;
          let curZ = 0;
          let curY = 0.15;

          const segments = 4;
          for (let s = 0; s < segments; s++) {
            const nextX = curX + Math.cos(rootAngle + (Math.random() - 0.5) * 0.6) * 0.8;
            const nextZ = curZ + Math.sin(rootAngle + (Math.random() - 0.5) * 0.6) * 0.8;
            const nextY = 0.08 + Math.random() * 0.15;

            tendrilPositions.push(curX, curY, curZ, nextX, nextY, nextZ);
            curX = nextX;
            curZ = nextZ;
            curY = nextY;
          }
        }

        const tendrilGeom = new THREE.BufferGeometry();
        tendrilGeom.setAttribute('position', new THREE.Float32BufferAttribute(tendrilPositions, 3));
        const tendrilMat = new THREE.LineBasicMaterial({
          color: isLightMode ? 0x9a3412 : 0xf59e0b, // Dark rust in Light Mode
          transparent: true,
          opacity: isLightMode ? 0.85 : 0.6,
          blending: isLightMode ? THREE.NormalBlending : THREE.AdditiveBlending,
        });
        const tendrils = new THREE.LineSegments(tendrilGeom, tendrilMat);
        firmPivot.add(tendrils);

        // Warm Hearth Light
        const hearthLight = new THREE.PointLight(
          isLightMode ? 0xc2410c : 0xf59e0b, 
          isLightMode ? 1.2 : 2.6, 
          isLightMode ? 7.5 : 9.5
        );
        hearthLight.position.set(0, 0.8, 0);
        firmPivot.add(hearthLight);
        firmPivot.userData.hearthLight = hearthLight;

        // Translucent Hit Sphere for effortless raycast selection
        const hitGeom = new THREE.SphereGeometry(2.6, 8, 8);
        const hitMat = new THREE.MeshBasicMaterial({
          color: isLightMode ? 0xc2410c : 0xf59e0b,
          transparent: true,
          opacity: 0.001,
          wireframe: false,
        });
        const hitMesh = new THREE.Mesh(hitGeom, hitMat);
        hitMesh.userData = { firmId: firm.id };
        firmPivot.add(hitMesh);
      }

      firmsGroup.add(firmPivot);
    });
  }, [firms, country, selectedFirm, scenario, theme]);

  return (
    <div className="relative w-full h-full overflow-hidden select-none">
      {/* Three.js Canvas Container */}
      <div ref={containerRef} className="w-full h-full cursor-grab active:cursor-grabbing" />
    </div>
  );
};
