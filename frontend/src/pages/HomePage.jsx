import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Dropzone from '../components/Dropzone';
import ProgressBar from '../components/ProgressBar';
import AnalysisCard from '../components/AnalysisCard';
import DependenciesList from '../components/DependenciesList';
import EntrypointSelector from '../components/EntrypointSelector';
import CommandOutput from '../components/CommandOutput';
import StepsCarousel from '../components/StepsCarousel';
import ProjectShowcase from '../components/ProjectShowcase';
import { 
  uploadProject,
  uploadFolder,
  getProject, 
  selectEntrypoint, 
  updateDependencies, 
  generateInstallers 
} from '../api/client';
import { Terminal, Shield, Zap, Loader2, Plus, Sparkles } from 'lucide-react';

export default function HomePage({ initialProjectId, onNavigate }) {
  const [stage, setStage] = useState('upload'); // 'upload' | 'analyzing' | 'results' | 'command'
  const [analysisProgressStep, setAnalysisProgressStep] = useState(1);
  const [projectRecord, setProjectRecord] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [plan, setPlan] = useState(null);
  const [commands, setCommands] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [isLoadingShared, setIsLoadingShared] = useState(false);

  // Modals
  const [isDepsModalOpen, setIsDepsModalOpen] = useState(false);
  const [isEntryModalOpen, setIsEntryModalOpen] = useState(false);

  // Check URL query param ?p=PROJECT_ID or ?project=PROJECT_ID on load, or initialProjectId prop
  useEffect(() => {
    if (initialProjectId) {
      loadSharedProject(initialProjectId.trim());
      return;
    }
    const params = new URLSearchParams(window.location.search);
    const sharedId = params.get('p') || params.get('project');
    if (sharedId) {
      loadSharedProject(sharedId.trim());
    }
  }, [initialProjectId]);

  const loadSharedProject = async (projectId) => {
    setIsLoadingShared(true);
    setUploadError(null);
    try {
      const details = await getProject(projectId);
      setProjectRecord({
        id: details.record?.id || details.id,
        original_filename: details.record?.original_filename || details.original_filename,
        status: details.record?.status || details.status,
        analysis: details.record?.analysis || details.analysis,
      });
      setAnalysis(details.record?.analysis || details.analysis);
      setPlan(details.plan);
      setCommands(details.installer_commands);
      
      // Update URL with shareable ?p=PROJECT_ID
      const newUrl = `${window.location.pathname}?p=${projectId}`;
      window.history.pushState({ projectId }, '', newUrl);

      // Scroll to top
      window.scrollTo({ top: 0, behavior: 'smooth' });

      // If plan and commands exist, go straight to command screen
      if (details.installer_commands && details.plan) {
        setStage('command');
      } else {
        setStage('results');
      }
    } catch (err) {
      setUploadError(`Could not load shared project (${projectId}): ${err.message}`);
      setStage('upload');
    } finally {
      setIsLoadingShared(false);
    }
  };

  const handleFileSelected = async (fileOrFiles, metadata = {}) => {
    setUploadError(null);
    setStage('analyzing');
    setAnalysisProgressStep(1);

    try {
      const stepTimer1 = setTimeout(() => setAnalysisProgressStep(2), 500);
      const stepTimer2 = setTimeout(() => setAnalysisProgressStep(3), 1100);
      const stepTimer3 = setTimeout(() => setAnalysisProgressStep(4), 1700);

      // If it's an array of files, use the folder upload endpoint
      const record = Array.isArray(fileOrFiles)
        ? await uploadFolder(fileOrFiles, metadata)
        : await uploadProject(fileOrFiles, metadata);
      
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);

      setProjectRecord(record);
      setAnalysis(record.analysis);

      // Update URL with shareable ?p=PROJECT_ID
      const newUrl = `${window.location.pathname}?p=${record.id}`;
      window.history.pushState({ projectId: record.id }, '', newUrl);

      const details = await getProject(record.id);
      setPlan(details.plan);
      setCommands(details.installer_commands);

      // Scroll to top
      window.scrollTo({ top: 0, behavior: 'smooth' });

      setStage('results');
    } catch (err) {
      setUploadError(err.message || 'Failed to upload and analyze project.');
      setStage('upload');
    }
  };

  const handleGenerate = async () => {
    if (!projectRecord) return;
    setIsGenerating(true);
    try {
      const res = await generateInstallers(projectRecord.id);
      setPlan(res.plan);
      setCommands(res.installer_commands);
      setStage('command');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      alert('Error generating installer: ' + err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSelectEntrypoint = async (entryPoint) => {
    if (!projectRecord) return;
    try {
      await selectEntrypoint(projectRecord.id, entryPoint);
      setAnalysis(prev => ({
        ...prev,
        entry_point: entryPoint,
        is_ambiguous_entrypoint: false,
      }));
    } catch (err) {
      alert('Failed to update entrypoint: ' + err.message);
    }
  };

  const handleUpdateDependencies = async (updatedDeps) => {
    if (!projectRecord) return;
    try {
      const res = await updateDependencies(projectRecord.id, updatedDeps);
      setAnalysis(prev => ({
        ...prev,
        dependencies: res.dependencies,
      }));
    } catch (err) {
      alert('Failed to update dependencies: ' + err.message);
    }
  };

  const handleReset = () => {
    setStage('upload');
    setProjectRecord(null);
    setAnalysis(null);
    setPlan(null);
    setCommands(null);
    setUploadError(null);
    window.history.pushState({}, '', window.location.pathname);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-[#fafafa] flex flex-col font-sans text-ink-900 relative">
      <Navbar onReset={handleReset} hasProject={stage !== 'upload'} currentPage="home" onNavigate={onNavigate} />

      {/* Floating Corner "+ New Project" Button */}
      {stage !== 'upload' && (
        <button
          onClick={handleReset}
          className="fixed bottom-6 right-6 z-40 inline-flex items-center gap-2 px-4 py-2.5 rounded-full bg-ink-950 hover:bg-ink-900 text-white font-medium text-xs font-sans shadow-paper-lg transition-transform hover:scale-105 cursor-pointer"
          title="Upload New Project"
        >
          <Plus className="w-4 h-4" />
          <span>New Project</span>
        </button>
      )}

      <main className="flex-1 max-w-4xl w-full mx-auto px-3 sm:px-6 py-6 sm:py-12 flex flex-col justify-center">
        {/* Loading Shared Project Screen */}
        {isLoadingShared && (
          <div className="py-16 sm:py-20 flex flex-col items-center justify-center space-y-4">
            <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
            <div className="text-center">
              <h3 className="text-base font-bold font-sans text-ink-950">Loading shared project...</h3>
              <p className="text-xs text-ink-500 font-sans mt-1">Retrieving analysis and installer commands</p>
            </div>
          </div>
        )}

        {/* Stage 1: Upload Hero, Dropzone, Carousel & Showcase */}
        {!isLoadingShared && stage === 'upload' && (
          <div className="space-y-8 sm:space-y-12">
            <div className="text-center max-w-2xl mx-auto space-y-3 sm:space-y-4">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-ink-100 border border-ink-200 text-ink-700 text-xs font-semibold">
                <span>Deterministic Installation Engine</span>
              </div>

              <h1 className="text-2xl sm:text-4xl md:text-5xl font-extrabold text-ink-950 tracking-tight leading-tight">
                One command that prepares any computer and runs your project.
              </h1>

              <p className="text-ink-600 text-xs sm:text-base md:text-lg leading-relaxed max-w-xl mx-auto">
                Upload your Python project as a folder or ZIP. We analyze runtime requirements, resolve dependencies, and generate a platform-specific bootstrap command for Windows, Linux, and macOS.
              </p>
            </div>

            {/* 4-Step Interactive Animated Carousel (Hero Showcase) */}
            <StepsCarousel />

            {/* Dropzone with Custom Project Name & Description */}
            <div className="space-y-4">
              <div className="text-center space-y-1">
                <h2 className="text-xl sm:text-2xl font-bold font-sans text-ink-950 tracking-tight">
                  Package Your Project Now
                </h2>
                <p className="text-xs text-ink-500 font-sans">
                  Drop your folder or archive below to generate your custom installer.
                </p>
              </div>

              <Dropzone
                onFileSelected={handleFileSelected}
                isUploading={stage === 'analyzing'}
                error={uploadError}
              />
            </div>

            {/* Community Projects Library & Marketplace Showcase */}
            <ProjectShowcase onSelectProject={loadSharedProject} />
          </div>
        )}

        {/* Stage 2: Active Analysis Progress */}
        {stage === 'analyzing' && (
          <div className="py-12">
            <ProgressBar currentStep={analysisProgressStep} statusText="Analyzing Project Structure..." />
          </div>
        )}

        {/* Stage 3: Analysis Card / Review */}
        {stage === 'results' && (
          <div className="space-y-6">
            <AnalysisCard
              analysis={analysis}
              onGenerate={handleGenerate}
              onOpenDependencies={() => setIsDepsModalOpen(true)}
              onOpenEntrypointSelector={() => setIsEntryModalOpen(true)}
              isGenerating={isGenerating}
            />
          </div>
        )}

        {/* Stage 4: Generated Command Screen */}
        {stage === 'command' && (
          <div className="space-y-6">
            <CommandOutput
              projectId={projectRecord?.id}
              commands={commands}
              plan={plan}
              onReset={handleReset}
            />
          </div>
        )}
      </main>

      {/* Dependencies Review Modal */}
      {isDepsModalOpen && analysis && (
        <DependenciesList
          dependencies={analysis.dependencies}
          source={analysis.dependency_source}
          onSave={handleUpdateDependencies}
          onClose={() => setIsDepsModalOpen(false)}
        />
      )}

      {/* Entry Point Selector Modal */}
      {isEntryModalOpen && analysis && (
        <EntrypointSelector
          candidates={analysis.candidate_entry_points}
          currentEntrypoint={analysis.entry_point}
          onSelect={handleSelectEntrypoint}
          onClose={() => setIsEntryModalOpen(false)}
        />
      )}

      {/* Footer */}
      <footer className="border-t border-ink-200 py-6 text-center text-xs text-ink-500 bg-white">
        <div className="max-w-4xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© 2026 One-Command Project Installer</p>
          <div className="flex items-center gap-4 text-ink-500">
            <span>PowerShell & POSIX Compliant</span>
            <span>•</span>
            <span>Zero Remote Execution Risk</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
