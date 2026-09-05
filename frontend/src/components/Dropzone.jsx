import React, { useState, useRef } from 'react';
import { Upload, FolderUp, FileArchive, ArrowRight, Sparkles, AlertCircle, Code, Cpu, Layers, Folder, Shield, Lock, Globe } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Dropzone({ onFileSelected, isUploading, error }) {
  const { user } = useAuth();
  const [isDragOver, setIsDragOver] = useState(false);
  const [isPackagingFolder, setIsPackagingFolder] = useState(false);
  const [packagingStatus, setPackagingStatus] = useState('');
  const [customProjectName, setCustomProjectName] = useState('');
  const [customDescription, setCustomDescription] = useState('');
  const [isPrivate, setIsPrivate] = useState(true);
  const [showDetailsForm, setShowDetailsForm] = useState(false);
  const fileInputRef = useRef(null);
  const folderInputRef = useRef(null);

  const getMetadata = () => ({
    projectName: customProjectName.trim() || undefined,
    description: customDescription.trim() || undefined,
    userId: user?.id || undefined,
    userEmail: user?.email || undefined,
    isPublic: user ? !isPrivate : true,
  });

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragOver(false);

    const items = e.dataTransfer.items;
    if (items && items.length > 0) {
      // Check if dropped item is a directory
      const entry = items[0].webkitGetAsEntry ? items[0].webkitGetAsEntry() : null;
      if (entry && entry.isDirectory) {
        await processDroppedFolder(entry);
        return;
      }
    }

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.name.toLowerCase().endsWith('.zip')) {
        validateAndPass(file);
      } else {
        // If user dropped multiple loose files or a folder without webkitGetAsEntry
        onFileSelected(Array.from(files), getMetadata());
      }
    }
  };

  const handleZipInput = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      validateAndPass(files[0]);
    }
  };

  const handleFolderInput = async (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const fileList = Array.from(files);
      onFileSelected(fileList, getMetadata());
    }
  };

  const validateAndPass = (file) => {
    if (file.size > 50 * 1024 * 1024) {
      alert('File size exceeds 50MB limit.');
      return;
    }
    onFileSelected(file, getMetadata());
  };

  // Recursively traverses a dropped FileSystemDirectoryEntry
  const processDroppedFolder = async (dirEntry) => {
    setIsPackagingFolder(true);
    setPackagingStatus(`Reading folder '${dirEntry.name}'...`);

    try {
      const fileEntries = await scanDirectory(dirEntry);
      if (fileEntries.length === 0) {
        alert('The dropped folder is empty.');
        setIsPackagingFolder(false);
        return;
      }

      setPackagingStatus(`Uploading ${fileEntries.length} files...`);
      
      // Convert scanned entries to File objects with relative paths set
      // We use the dirEntry.name as the root folder name
      const filesWithPaths = fileEntries.map(entry => {
        const relativePath = `${dirEntry.name}/${entry.path}`;
        // Create a new File with the relative path as the name
        const newFile = new File([entry.file], relativePath, { type: entry.file.type });
        // Attach webkitRelativePath for the upload function
        Object.defineProperty(newFile, 'webkitRelativePath', {
          value: relativePath,
          writable: false,
        });
        return newFile;
      });

      setIsPackagingFolder(false);
      onFileSelected(filesWithPaths);
    } catch (err) {
      alert('Failed to read folder: ' + err.message);
      setIsPackagingFolder(false);
    }
  };

  const loadSampleProject = async (type) => {
    let zipData;
    let filename;

    if (type === 'fastapi') {
      filename = 'fastapi-service.zip';
      zipData = await createSampleZip({
        'main.py': `from fastapi import FastAPI\nimport uvicorn\n\napp = FastAPI(title="Demo API")\n\n@app.get("/")\ndef root():\n    return {"message": "Hello from One-Command FastAPI!"}\n\nif __name__ == "__main__":\n    uvicorn.run(app, host="0.0.0.0", port=8000)\n`,
        'requirements.txt': 'fastapi>=0.100.0\nuvicorn[standard]>=0.23.0\npydantic>=2.0\n',
      });
    } else if (type === 'inferred') {
      filename = 'data-science-tool.zip';
      zipData = await createSampleZip({
        'app.py': `import numpy as np\nimport pandas as pd\nimport cv2\nfrom PIL import Image\nimport math\n\ndef process():\n    arr = np.zeros((100, 100, 3), dtype=np.uint8)\n    print("Data science pipeline executed successfully!")\n\nif __name__ == "__main__":\n    process()\n`,
        'utils.py': `def helper():\n    return 42\n`,
      });
    } else if (type === 'web') {
      filename = 'html5-tailwind-app.zip';
      zipData = await createSampleZip({
        'index.html': `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Modern Tailwind Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <link rel="stylesheet" href="style.css">
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen p-8">
  <div class="max-w-3xl mx-auto space-y-4">
    <div class="p-6 bg-slate-800 rounded-2xl border border-slate-700 shadow-xl">
      <h1 class="text-2xl font-bold text-indigo-400">✨ One-Command Web Application</h1>
      <p class="text-sm text-slate-400 mt-1">HTML5 + Tailwind CSS + Lucide Icons</p>
    </div>
  </div>
  <script src="app.js"></script>
</body>
</html>`,
        'style.css': `body { font-family: system-ui, -apple-system, sans-serif; }\n`,
        'app.js': `console.log("One-Command Web App initialized successfully!");\n`,
      });
    } else if (type === 'ambiguous') {
      filename = 'multi-entrypoint-app.zip';
      zipData = await createSampleZip({
        'main.py': `import sys\nif __name__ == "__main__":\n    print("Main script starting...")\n`,
        'server.py': `import sys\nif __name__ == "__main__":\n    print("Server worker starting...")\n`,
        'requirements.txt': 'requests>=2.28.0\n',
      });
    }

    if (zipData) {
      const file = new File([zipData], filename, { type: 'application/zip' });
      onFileSelected(file);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      {/* Upload Box */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`relative rounded-2xl p-5 sm:p-10 text-center transition-all bg-white border-2 border-dashed ${
          isDragOver
            ? 'border-ink-950 bg-ink-50 scale-[1.005] shadow-paper-md'
            : 'border-ink-300 hover:border-ink-400 hover:bg-ink-50/50 shadow-paper'
        }`}
      >
        {/* Hidden inputs */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".zip"
          onChange={handleZipInput}
          className="hidden"
        />
        <input
          ref={folderInputRef}
          type="file"
          webkitdirectory="true"
          directory="true"
          multiple
          onChange={handleFolderInput}
          className="hidden"
        />

        <div className="flex items-center justify-center gap-2 mb-4">
          <div className="w-11 h-11 rounded-lg bg-ink-100 border border-ink-200 flex items-center justify-center text-ink-900 shadow-paper-sm">
            <Folder className="w-5 h-5" />
          </div>
          <span className="text-ink-300 text-xs font-mono font-medium">+</span>
          <div className="w-11 h-11 rounded-lg bg-ink-100 border border-ink-200 flex items-center justify-center text-ink-900 shadow-paper-sm">
            <FileArchive className="w-5 h-5" />
          </div>
        </div>

        <h2 className="text-xl sm:text-2xl font-bold font-sans text-ink-950 mb-2 tracking-tight">
          Drop your project folder or ZIP archive
        </h2>
        <p className="text-ink-600 font-sans text-sm max-w-md mx-auto mb-6 leading-relaxed">
          Drop any Python, HTML/CSS, React, Vite, or Full-Stack project folder or <span className="font-mono text-ink-900 bg-ink-100 px-1 py-0.5 rounded text-xs">.zip</span>. We'll automatically detect dependencies, runtime requirements, and entry points.
        </p>

        {isPackagingFolder ? (
          <div className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-ink-100 text-ink-900 text-xs sm:text-sm font-medium font-sans animate-pulse">
            <span>{packagingStatus}</span>
          </div>
        ) : (
          <div className="flex flex-col sm:flex-row items-center justify-center gap-2.5 w-full sm:w-auto">
            <button
              type="button"
              onClick={() => folderInputRef.current?.click()}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-3 sm:py-2.5 rounded-xl sm:rounded-lg bg-ink-950 hover:bg-ink-900 text-white text-xs sm:text-sm font-medium shadow-paper-sm transition-colors font-sans cursor-pointer active:scale-95"
            >
              <FolderUp className="w-4 h-4" />
              <span>Select Project Folder</span>
            </button>

            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-3 sm:py-2.5 rounded-xl sm:rounded-lg bg-white hover:bg-ink-100 border border-ink-300 text-ink-800 text-xs sm:text-sm font-medium shadow-paper-sm transition-colors font-sans cursor-pointer active:scale-95"
            >
              <FileArchive className="w-4 h-4" />
              <span>Select ZIP File</span>
            </button>
          </div>
        )}

        {/* Optional Project Info Customization */}
        <div className="mt-4 pt-3 border-t border-dashed border-ink-200 max-w-md mx-auto text-left">
          <button
            type="button"
            onClick={(e) => { e.stopPropagation(); setShowDetailsForm(!showDetailsForm); }}
            className="text-xs font-semibold text-indigo-700 hover:text-indigo-900 font-sans flex items-center gap-1 mx-auto cursor-pointer"
          >
            <span>{showDetailsForm ? '− Hide Custom Name & Description' : '+ Add Custom Name & Description (Optional)'}</span>
          </button>

          {showDetailsForm && (
            <div className="mt-3 space-y-3 p-3.5 bg-ink-50 rounded-xl border border-ink-200 animate-scale-in" onClick={(e) => e.stopPropagation()}>
              <div>
                <label className="block text-[11px] font-bold font-sans text-ink-900 mb-1">Project Name (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. Speech AI Service"
                  value={customProjectName}
                  onChange={(e) => setCustomProjectName(e.target.value)}
                  className="w-full px-3 py-1.5 rounded-lg bg-white border border-ink-300 text-xs font-sans text-ink-950 focus:outline-none focus:border-ink-500 transition-colors"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold font-sans text-ink-900 mb-1">Short Description (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. Real-time voice modulation API built with FastAPI"
                  value={customDescription}
                  onChange={(e) => setCustomDescription(e.target.value)}
                  className="w-full px-3 py-1.5 rounded-lg bg-white border border-ink-300 text-xs font-sans text-ink-950 focus:outline-none focus:border-ink-500 transition-colors"
                />
              </div>

              {/* Privacy Setting */}
              <div>
                <label className="block text-[11px] font-bold font-sans text-ink-900 mb-1.5">Package Privacy</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setIsPrivate(true)}
                    className={`flex items-center justify-center gap-1.5 p-2 rounded-lg border text-xs font-medium font-sans transition-all cursor-pointer ${
                      isPrivate
                        ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                        : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    <Lock className="w-3.5 h-3.5" />
                    <span>Private Package</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setIsPrivate(false)}
                    className={`flex items-center justify-center gap-1.5 p-2 rounded-lg border text-xs font-medium font-sans transition-all cursor-pointer ${
                      !isPrivate
                        ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                        : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    <Globe className="w-3.5 h-3.5" />
                    <span>Public Showcase</span>
                  </button>
                </div>
                <p className="text-[10px] text-slate-500 font-sans mt-1">
                  {isPrivate ? 'Only accessible by you when signed in.' : 'Visible in the community showcase repository library.'}
                </p>
              </div>
            </div>
          )}
        </div>

        <div className="mt-5 flex flex-wrap items-center justify-center gap-4 text-xs text-ink-500 font-sans">
          <span>Python & Web Projects</span>
          <span>•</span>
          <span>Folder & ZIP Supported</span>
          <span>•</span>
          <span>Zip-Slip Protected</span>
        </div>
      </div>

      {/* Error message if any */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 flex items-start gap-3 text-rose-900 text-sm">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-rose-950 font-sans">Upload Error</p>
            <p className="text-rose-800 text-xs mt-0.5 font-sans">{error}</p>
          </div>
        </div>
      )}

      {/* Try with Sample Projects */}
      <div className="p-5 rounded-xl bg-white border border-ink-200 shadow-paper">
        <div className="flex items-center gap-2 mb-3 text-ink-700 text-xs font-semibold uppercase tracking-wider font-sans">
          <Sparkles className="w-3.5 h-3.5 text-ink-900" />
          <span>Or test instantly with sample repositories:</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <button
            type="button"
            disabled={isUploading || isPackagingFolder}
            onClick={(e) => { e.stopPropagation(); loadSampleProject('fastapi'); }}
            className="flex items-center gap-3 p-3 rounded-lg border border-ink-200 bg-ink-50/50 hover:bg-ink-100 hover:border-ink-300 text-left transition-all group disabled:opacity-50 cursor-pointer"
          >
            <div className="w-8 h-8 rounded-md bg-white border border-ink-200 text-ink-800 flex items-center justify-center shrink-0 shadow-paper-sm">
              <Code className="w-4 h-4" />
            </div>
            <div>
              <p className="text-xs font-bold text-ink-950 font-sans group-hover:text-accent-blue">FastAPI Service</p>
              <p className="text-[11px] text-ink-500 font-mono">Python API</p>
            </div>
          </button>

          <button
            type="button"
            disabled={isUploading || isPackagingFolder}
            onClick={(e) => { e.stopPropagation(); loadSampleProject('web'); }}
            className="flex items-center gap-3 p-3 rounded-lg border border-indigo-200 bg-indigo-50/40 hover:bg-indigo-100 hover:border-indigo-300 text-left transition-all group disabled:opacity-50 cursor-pointer"
          >
            <div className="w-8 h-8 rounded-md bg-white border border-indigo-200 text-indigo-700 flex items-center justify-center shrink-0 shadow-paper-sm">
              <Sparkles className="w-4 h-4 text-indigo-600" />
            </div>
            <div>
              <p className="text-xs font-bold text-indigo-950 font-sans group-hover:text-indigo-800">HTML5 + Tailwind</p>
              <p className="text-[11px] text-indigo-700 font-mono">Static Web App</p>
            </div>
          </button>

          <button
            type="button"
            disabled={isUploading || isPackagingFolder}
            onClick={(e) => { e.stopPropagation(); loadSampleProject('inferred'); }}
            className="flex items-center gap-3 p-3 rounded-lg border border-ink-200 bg-ink-50/50 hover:bg-ink-100 hover:border-ink-300 text-left transition-all group disabled:opacity-50 cursor-pointer"
          >
            <div className="w-8 h-8 rounded-md bg-white border border-ink-200 text-ink-800 flex items-center justify-center shrink-0 shadow-paper-sm">
              <Cpu className="w-4 h-4" />
            </div>
            <div>
              <p className="text-xs font-bold text-ink-950 font-sans group-hover:text-accent-blue">Data Science</p>
              <p className="text-[11px] text-ink-500 font-mono">AST Inferred</p>
            </div>
          </button>

          <button
            type="button"
            disabled={isUploading || isPackagingFolder}
            onClick={(e) => { e.stopPropagation(); loadSampleProject('ambiguous'); }}
            className="flex items-center gap-3 p-3 rounded-lg border border-ink-200 bg-ink-50/50 hover:bg-ink-100 hover:border-ink-300 text-left transition-all group disabled:opacity-50 cursor-pointer"
          >
            <div className="w-8 h-8 rounded-md bg-white border border-ink-200 text-ink-800 flex items-center justify-center shrink-0 shadow-paper-sm">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <p className="text-xs font-bold text-ink-950 font-sans group-hover:text-accent-blue">Multi-Entry</p>
              <p className="text-[11px] text-ink-500 font-mono">Ambiguity Test</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}

// Recursively scans a FileSystemDirectoryEntry and returns array of { path, file }
async function scanDirectory(dirEntry, currentPath = '') {
  const entries = [];
  const dirReader = dirEntry.createReader();

  const readEntries = () => {
    return new Promise((resolve, reject) => {
      dirReader.readEntries(resolve, reject);
    });
  };

  let readBatch = await readEntries();
  const allChildren = [];
  while (readBatch.length > 0) {
    allChildren.push(...readBatch);
    readBatch = await readEntries();
  }

  for (const child of allChildren) {
    const childPath = currentPath ? `${currentPath}/${child.name}` : child.name;
    if (child.isFile) {
      const file = await getFileFromEntry(child);
      entries.push({ path: childPath, file });
    } else if (child.isDirectory) {
      const subEntries = await scanDirectory(child, childPath);
      entries.push(...subEntries);
    }
  }

  return entries;
}

function getFileFromEntry(fileEntry) {
  return new Promise((resolve, reject) => {
    fileEntry.file(resolve, reject);
  });
}


async function createSampleZip(filesMap) {
  const fileEntries = Object.entries(filesMap);
  const parts = [];
  const centralDirectory = [];
  let offset = 0;
  const textEncoder = new TextEncoder();

  for (const [filename, content] of fileEntries) {
    const filenameBytes = textEncoder.encode(filename);
    const contentBytes = textEncoder.encode(content);
    const crc = crc32(contentBytes);
    const size = contentBytes.length;

    const localHeader = new Uint8Array(30 + filenameBytes.length);
    const view = new DataView(localHeader.buffer);
    view.setUint32(0, 0x04034b50, true);
    view.setUint16(4, 20, true);
    view.setUint16(6, 0, true);
    view.setUint16(8, 0, true);
    view.setUint16(10, 0, true);
    view.setUint16(12, 0, true);
    view.setUint32(14, crc, true);
    view.setUint32(18, size, true);
    view.setUint32(22, size, true);
    view.setUint16(26, filenameBytes.length, true);
    view.setUint16(28, 0, true);
    localHeader.set(filenameBytes, 30);

    parts.push(localHeader);
    parts.push(contentBytes);

    const cdHeader = new Uint8Array(46 + filenameBytes.length);
    const cdView = new DataView(cdHeader.buffer);
    cdView.setUint32(0, 0x02014b50, true);
    cdView.setUint16(4, 20, true);
    cdView.setUint16(6, 20, true);
    cdView.setUint16(8, 0, true);
    cdView.setUint16(10, 0, true);
    cdView.setUint16(12, 0, true);
    cdView.setUint16(14, 0, true);
    cdView.setUint32(16, crc, true);
    cdView.setUint32(20, size, true);
    cdView.setUint32(24, size, true);
    cdView.setUint16(28, filenameBytes.length, true);
    cdView.setUint16(30, 0, true);
    cdView.setUint16(32, 0, true);
    cdView.setUint16(34, 0, true);
    cdView.setUint16(36, 0, true);
    cdView.setUint32(38, 0, true);
    cdView.setUint32(42, offset, true);
    cdHeader.set(filenameBytes, 46);

    centralDirectory.push(cdHeader);
    offset += localHeader.length + contentBytes.length;
  }

  const cdOffset = offset;
  let cdSize = 0;
  for (const cd of centralDirectory) {
    parts.push(cd);
    cdSize += cd.length;
  }

  const eocd = new Uint8Array(22);
  const eocdView = new DataView(eocd.buffer);
  eocdView.setUint32(0, 0x06054b50, true);
  eocdView.setUint16(4, 0, true);
  eocdView.setUint16(6, 0, true);
  eocdView.setUint16(8, fileEntries.length, true);
  eocdView.setUint16(10, fileEntries.length, true);
  eocdView.setUint32(12, cdSize, true);
  eocdView.setUint32(16, cdOffset, true);
  eocdView.setUint16(20, 0, true);
  parts.push(eocd);

  return new Blob(parts, { type: 'application/zip' });
}

function crc32(buf) {
  let crc = 0 ^ (-1);
  for (let i = 0; i < buf.length; i++) {
    crc = (crc >>> 8) ^ table[(crc ^ buf[i]) & 0xFF];
  }
  return (crc ^ (-1)) >>> 0;
}

const table = (() => {
  let c;
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    c = n;
    for (let k = 0; k < 8; k++) {
      c = ((c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1));
    }
    t[n] = c;
  }
  return t;
})();
