// 📁 browser_extension/content_script.js
/**
 * OFF-CAMPUS JOB ASSISTANT - Content Script
 * Injects assistant features into job portals
 */

class OffCampusAssistant {
    constructor() {
        this.jobData = null;
        this.isActive = false;
        this.applicationHistory = [];
        this.initAssistant();
    }

    initAssistant() {
        console.log('🟢 Off-Campus Assistant Initialized');
        
        // Inject assistant UI
        this.injectAssistantUI();
        
        // Listen for messages
        this.setupMessageListener();
        
        // Observe page changes for SPA
        this.setupPageObserver();
        
        // Load application history
        this.loadApplicationHistory();
    }

    injectAssistantUI() {
        // Create assistant sidebar
        const sidebar = document.createElement('div');
        sidebar.id = 'offcampus-sidebar';
        sidebar.innerHTML = `
            <div class="offcampus-header">
                <h3>🎯 Off-Campus Assistant</h3>
                <button id="offcampus-toggle">−</button>
            </div>
            <div class="offcampus-content">
                <div class="job-analysis">
                    <h4>Job Analysis</h4>
                    <div id="match-score">Match: --%</div>
                    <div id="skills-found">Skills: --</div>
                </div>
                <div class="quick-actions">
                    <button id="analyze-job" class="btn-primary">🔍 Analyze Job</button>
                    <button id="quick-apply" class="btn-success">⚡ Quick Apply</button>
                    <button id="save-job" class="btn-secondary">💾 Save for Later</button>
                </div>
                <div class="application-stats">
                    <h4>Today's Stats</h4>
                    <div>Applied: <span id="applied-today">0</span></div>
                    <div>Saved: <span id="saved-today">0</span></div>
                </div>
            </div>
        `;
        
        document.body.appendChild(sidebar);
        
        // Add event listeners
        this.attachEventListeners();
    }

    attachEventListeners() {
        // Analyze Job Button
        document.getElementById('analyze-job').addEventListener('click', () => {
            this.analyzeCurrentJob();
        });

        // Quick Apply Button
        document.getElementById('quick-apply').addEventListener('click', () => {
            this.initiateQuickApply();
        });

        // Toggle Sidebar
        document.getElementById('offcampus-toggle').addEventListener('click', () => {
            this.toggleSidebar();
        });
    }

    analyzeCurrentJob() {
        const jobData = this.extractJobData();
        
        // Send to background for AI analysis
        chrome.runtime.sendMessage({
            action: 'analyzeJob',
            jobData: jobData,
            source: 'offcampus_assistant'
        }, (response) => {
            this.displayAnalysisResults(response);
        });
    }

    extractJobData() {
        // Extract job data based on current portal
        const portal = this.detectCurrentPortal();
        let jobData = {};

        switch(portal) {
            case 'linkedin':
                jobData = this.extractLinkedInJob();
                break;
            case 'indeed':
                jobData = this.extractIndeedJob();
                break;
            case 'glassdoor':
                jobData = this.extractGlassdoorJob();
                break;
        }

        jobData.portal = portal;
        jobData.url = window.location.href;
        jobData.timestamp = new Date().toISOString();

        return jobData;
    }

    extractLinkedInJob() {
        return {
            title: document.querySelector('.jobs-details-top-card__job-title')?.textContent?.trim() || '',
            company: document.querySelector('.jobs-details-top-card__company-url')?.textContent?.trim() || '',
            location: document.querySelector('.jobs-details-top-card__bullet')?.textContent?.trim() || '',
            description: document.querySelector('.jobs-description__content')?.textContent?.trim() || '',
            easyApply: !!document.querySelector('.jobs-apply-button'),
            postedDate: this.extractPostedDate(),
            seniorityLevel: this.extractSeniorityLevel()
        };
    }

    initiateQuickApply() {
        // Check if Easy Apply is available
        const easyApplyBtn = document.querySelector('.jobs-apply-button');
        
        if (easyApplyBtn) {
            easyApplyBtn.click();
            
            // Wait for modal and auto-fill
            setTimeout(() => {
                this.autoFillApplication();
            }, 2000);
        } else {
            this.showNotification('No Easy Apply option available', 'warning');
        }
    }

    autoFillApplication() {
        // Auto-fill LinkedIn Easy Apply form
        const fields = this.detectFormFields();
        
        chrome.storage.local.get(['offcampusProfile'], (result) => {
            const profile = result.offcampusProfile || {};
            
            // Fill form fields
            fields.forEach(field => {
                this.fillField(field, profile);
            });
            
            // Save application attempt
            this.saveApplicationAttempt('auto_fill');
            
            this.showNotification('Form auto-filled successfully!', 'success');
        });
    }

    displayAnalysisResults(analysis) {
        // Update sidebar with analysis
        document.getElementById('match-score').textContent = `Match: ${analysis.matchScore}%`;
        document.getElementById('skills-found').textContent = `Skills: ${analysis.matchedSkills.length}`;
        
        // Show detailed analysis modal
        this.showAnalysisModal(analysis);
    }

    showAnalysisModal(analysis) {
        const modal = document.createElement('div');
        modal.className = 'offcampus-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>🎯 Job Match Analysis</h3>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="score-breakdown">
                        <div class="score-item">
                            <span class="score-label">Overall Match</span>
                            <span class="score-value ${analysis.matchScore > 70 ? 'high' : analysis.matchScore > 40 ? 'medium' : 'low'}">
                                ${analysis.matchScore}%
                            </span>
                        </div>
                        <div class="score-item">
                            <span class="score-label">Skills Match</span>
                            <span class="score-value">${analysis.skillMatch}%</span>
                        </div>
                    </div>
                    
                    <div class="skills-section">
                        <h4>✅ Matched Skills</h4>
                        <div class="skills-list">
                            ${analysis.matchedSkills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                        </div>
                    </div>
                    
                    ${analysis.missingSkills.length > 0 ? `
                    <div class="skills-section">
                        <h4>⚠️ Missing Skills</h4>
                        <div class="skills-list">
                            ${analysis.missingSkills.map(skill => `<span class="skill-tag missing">${skill}</span>`).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    <div class="recommendation">
                        <h4>💡 Recommendation</h4>
                        <p>${this.getRecommendation(analysis.matchScore)}</p>
                    </div>
                </div>
                <div class="modal-footer">
                    <button id="apply-anyway" class="btn-primary">Apply Anyway</button>
                    <button id="close-analysis" class="btn-secondary">Close</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add modal event listeners
        modal.querySelector('.close-modal').addEventListener('click', () => modal.remove());
        modal.querySelector('#close-analysis').addEventListener('click', () => modal.remove());
        modal.querySelector('#apply-anyway').addEventListener('click', () => {
            this.initiateQuickApply();
            modal.remove();
        });
    }

    getRecommendation(score) {
        if (score >= 80) return "Excellent match! Strongly recommended to apply.";
        if (score >= 60) return "Good match. Recommended to apply.";
        if (score >= 40) return "Moderate match. Consider applying if interested.";
        return "Low match. Consider applying only if desperate.";
    }

    detectCurrentPortal() {
        const url = window.location.href;
        if (url.includes('linkedin.com')) return 'linkedin';
        if (url.includes('indeed.com')) return 'indeed';
        if (url.includes('glassdoor.com')) return 'glassdoor';
        return 'unknown';
    }
}

// Initialize the assistant
const offCampusAssistant = new OffCampusAssistant();