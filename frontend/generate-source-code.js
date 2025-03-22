const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const sourceDir = 'app';
const outFile = 'frontend-docs/source-code.md';

// Find all TypeScript files
const files = execSync(`find ${sourceDir} -type f -name "*.ts*" | sort`)
  .toString()
  .split('\n')
  .filter(Boolean);

// Generate markdown with all source code
let content = '# Sync Smart Home Frontend Source Code\n\n';

files.forEach(file => {
  try {
    const fileContent = fs.readFileSync(file, 'utf8');
    content += `## ${file}\n\n\`\`\`typescript\n${fileContent}\n\`\`\`\n\n`;
  } catch (err) {
    content += `## ${file}\n\nError reading file: ${err.message}\n\n`;
  }
});

// Write the markdown file
fs.writeFileSync(outFile, content);
console.log(`Source code documentation written to ${outFile}`);
