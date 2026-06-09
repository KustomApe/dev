// Run with: node generate_icons.js
// Generates simple PNG icons for the extension
const { createCanvas } = require('canvas');
const fs = require('fs');
const path = require('path');

function drawIcon(size) {
  const canvas = createCanvas(size, size);
  const ctx = canvas.getContext('2d');

  // Background circle
  ctx.beginPath();
  ctx.arc(size / 2, size / 2, size / 2, 0, Math.PI * 2);
  ctx.fillStyle = '#7c3aed';
  ctx.fill();

  // Panda face (simplified)
  const s = size / 128;

  // White face
  ctx.beginPath();
  ctx.arc(size / 2, size / 2 + 4 * s, 42 * s, 0, Math.PI * 2);
  ctx.fillStyle = '#ffffff';
  ctx.fill();

  // Left ear
  ctx.beginPath();
  ctx.arc(size / 2 - 28 * s, size / 2 - 24 * s, 16 * s, 0, Math.PI * 2);
  ctx.fillStyle = '#1a1a2e';
  ctx.fill();

  // Right ear
  ctx.beginPath();
  ctx.arc(size / 2 + 28 * s, size / 2 - 24 * s, 16 * s, 0, Math.PI * 2);
  ctx.fillStyle = '#1a1a2e';
  ctx.fill();

  // Left eye patch
  ctx.beginPath();
  ctx.ellipse(size / 2 - 14 * s, size / 2 - 2 * s, 11 * s, 9 * s, -0.3, 0, Math.PI * 2);
  ctx.fillStyle = '#1a1a2e';
  ctx.fill();

  // Right eye patch
  ctx.beginPath();
  ctx.ellipse(size / 2 + 14 * s, size / 2 - 2 * s, 11 * s, 9 * s, 0.3, 0, Math.PI * 2);
  ctx.fillStyle = '#1a1a2e';
  ctx.fill();

  // Eyes
  ctx.beginPath();
  ctx.arc(size / 2 - 14 * s, size / 2 - 2 * s, 4 * s, 0, Math.PI * 2);
  ctx.fillStyle = '#ffffff';
  ctx.fill();

  ctx.beginPath();
  ctx.arc(size / 2 + 14 * s, size / 2 - 2 * s, 4 * s, 0, Math.PI * 2);
  ctx.fillStyle = '#ffffff';
  ctx.fill();

  // Nose
  ctx.beginPath();
  ctx.ellipse(size / 2, size / 2 + 10 * s, 5 * s, 3.5 * s, 0, 0, Math.PI * 2);
  ctx.fillStyle = '#1a1a2e';
  ctx.fill();

  return canvas;
}

const sizes = [16, 32, 48, 128];
const dir = path.join(__dirname, 'icons');
if (!fs.existsSync(dir)) fs.mkdirSync(dir);

sizes.forEach(size => {
  const canvas = drawIcon(size);
  const buf = canvas.toBuffer('image/png');
  fs.writeFileSync(path.join(dir, `icon${size}.png`), buf);
  console.log(`Generated icon${size}.png`);
});
