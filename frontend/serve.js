const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 5175;
const DIST_DIR = path.join(__dirname);  // 直接使用当前目录

const mimeTypes = {
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

const server = http.createServer((req, res) => {
  console.log(`${req.method} ${req.url}`);
  
  // 移除查询字符串
  let filePath = req.url.split('?')[0];
  
  // 默认为 index.html
  if (filePath === '/') {
    filePath = '/index.html';
  }
  
  const fullPath = path.join(DIST_DIR, filePath);
  const ext = path.extname(fullPath);
  const contentType = mimeTypes[ext] || 'application/octet-stream';
  
  fs.readFile(fullPath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        // 文件不存在，返回 index.html (SPA 路由)
        fs.readFile(path.join(DIST_DIR, 'index.html'), (err2, content2) => {
          if (err2) {
            res.writeHead(500);
            res.end('Server Error');
          } else {
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(content2);
          }
        });
      } else {
        res.writeHead(500);
        res.end('Server Error');
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content);
    }
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running at http://localhost:${PORT}/`);
});
