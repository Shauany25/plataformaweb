// Servidor estático opcional para conferir o mesmo subdiretório usado no Pages.
import http from 'node:http';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const root = path.dirname(fileURLToPath(import.meta.url));
const base = '/plataformaweb/';
const pages = new Set(['index.html','ENEM.html','exercicio.html','tecnicas.html','conta.html','pesquisa.html']);
const types = {'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml','.pdf':'application/pdf'};
http.createServer(async (req,res) => {
  try {
    const pathname = new URL(req.url,'http://localhost').pathname;
    if (pathname === '/') {res.writeHead(302,{Location:base});res.end();return;}
    const file = decodeURIComponent(pathname.slice(base.length)) || 'index.html';
    if (!pathname.startsWith(base) || (!pages.has(file) && !file.startsWith('assets/')) ||
        file.split('/').some(segment => segment.startsWith('.')) || /[\\:]/.test(file)) throw Error();
    const content = await readFile(path.join(root,file));
    res.writeHead(200,{'Content-Type':types[path.extname(file)] || 'application/octet-stream','Cache-Control':'no-store'});
    res.end(content);
  } catch {res.writeHead(404);res.end();}
}).listen(8080,'127.0.0.1',()=>console.log('http://127.0.0.1:8080/plataformaweb/'));
