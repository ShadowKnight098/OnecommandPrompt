/**
 * API client for interacting with the One-Command backend.
 */

const API_BASE = import.meta.env.VITE_API_BASE || '';

// Directories to skip during folder uploads
const IGNORED_DIRS = ['.git', '__pycache__', '.pytest_cache', '.mypy_cache',
  '.venv', 'venv', 'env', 'node_modules', '.idea', '.vscode', '.hg', '.svn',
  'dist', 'build', '.egg-info', '.tox', '.nox'];

// Large binary/dataset extensions to skip (not needed for analysis)
const SKIP_EXTENSIONS = [
  '.csv', '.tsv', '.parquet', '.h5', '.hdf5', '.pkl', '.pickle',
  '.npy', '.npz', '.pt', '.pth', '.onnx', '.pb', '.tflite',
  '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.ico', '.svg',
  '.mp3', '.wav', '.flac', '.ogg', '.mp4', '.avi', '.mkv', '.mov', '.webm',
  '.zip', '.tar', '.gz', '.bz2', '.xz', '.rar', '.7z',
  '.db', '.sqlite', '.sqlite3',
  '.exe', '.dll', '.so', '.dylib', '.bin',
  '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
];

function shouldSkipFile(relativePath) {
  const parts = relativePath.replace(/\\/g, '/').split('/');
  // Skip files inside ignored directories
  for (const part of parts) {
    if (IGNORED_DIRS.includes(part)) return true;
  }
  // Skip large binary/dataset files by extension
  const ext = '.' + relativePath.split('.').pop().toLowerCase();
  if (SKIP_EXTENSIONS.includes(ext)) return true;
  return false;
}

export async function uploadProject(file, metadata = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 min timeout

  try {
    const formData = new FormData();
    formData.append('file', file);
    if (metadata.projectName) formData.append('project_name', metadata.projectName);
    if (metadata.description) formData.append('description', metadata.description);

    const response = await fetch(`${API_BASE}/api/projects/upload`, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
    }

    return response.json();
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error('Upload timed out. The project may be too large.');
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function uploadFolder(files, metadata = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 min timeout

  try {
    const formData = new FormData();
    let includedCount = 0;

    for (const file of files) {
      const relativePath = file.webkitRelativePath || file.name;
      // Skip dataset/binary files and ignored directories
      if (shouldSkipFile(relativePath)) continue;
      formData.append('files', file, relativePath);
      includedCount++;
    }

    if (includedCount === 0) {
      throw new Error('No Python source files found in the selected folder.');
    }

    if (metadata.projectName) formData.append('project_name', metadata.projectName);
    if (metadata.description) formData.append('description', metadata.description);

    const response = await fetch(`${API_BASE}/api/projects/upload-folder`, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Folder upload failed' }));
      throw new Error(errorData.detail || `Folder upload failed with status ${response.status}`);
    }

    return response.json();
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error('Upload timed out. Try selecting a smaller folder or removing large data files.');
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function listProjects(limit = 20) {
  const response = await fetch(`${API_BASE}/api/projects?limit=${limit}`);
  if (!response.ok) {
    throw new Error('Failed to fetch projects list');
  }
  return response.json();
}

export async function getProject(projectId) {
  const response = await fetch(`${API_BASE}/api/projects/${projectId}`);
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Failed to fetch project' }));
    throw new Error(err.detail || 'Project not found');
  }
  return response.json();
}

export async function selectEntrypoint(projectId, entryPoint) {
  const response = await fetch(`${API_BASE}/api/projects/${projectId}/entrypoint`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ entry_point: entryPoint }),
  });
  if (!response.ok) {
    throw new Error('Failed to set entrypoint');
  }
  return response.json();
}

export async function updateDependencies(projectId, dependencies) {
  const response = await fetch(`${API_BASE}/api/projects/${projectId}/dependencies`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dependencies }),
  });
  if (!response.ok) {
    throw new Error('Failed to update dependencies');
  }
  return response.json();
}

export async function generateInstallers(projectId, payload = {}) {
  const response = await fetch(`${API_BASE}/api/projects/${projectId}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error('Failed to generate installers');
  }
  return response.json();
}

export async function fetchScriptContent(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('Failed to load installer script');
  }
  return response.text();
}
