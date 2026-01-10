const fs = require('fs');
const path = require('path');

// Copy PDF to .next/static during build
const source = path.join(__dirname, '..', 'public', 'constitution.pdf');
const destDir = path.join(__dirname, '..', '.next', 'static');
const dest = path.join(destDir, 'constitution.pdf');

// Ensure .next/static exists
if (!fs.existsSync(destDir)) {
  fs.mkdirSync(destDir, { recursive: true });
}

// Copy the file
fs.copyFileSync(source, dest);
console.log('PDF copied to .next/static/constitution.pdf');
