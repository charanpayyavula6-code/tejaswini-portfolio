/**
 * PEMMASANI TEJASWINI - PORTFOLIO INTERACTION ENGINE
 * Built with Vanilla JavaScript (ES6+)
 */

document.addEventListener('DOMContentLoaded', () => {
  'use strict';

  // ==========================================================================
  // 1. DATA SOURCE OF TRUTH (Project Case Studies)
  // ==========================================================================
  let PROJECT_DATA = {
    'face-attendance': {
      title: 'Face Recognition Attendance System',
      category: 'Computer Vision & Database',
      overview: 'Developed a system for real-time face detection and recognition through a webcam using OpenCV and Python. Automated attendance marking to reduce manual effort and prevent proxy attendance.',
      problem: 'Traditional paper and manual attendance systems are time-consuming, prone to human error, and vulnerable to buddy punching / proxy attendance in institutional and enterprise environments.',
      solution: 'Built an end-to-end computer vision application using Python and OpenCV that captures live webcam video streams, identifies facial feature landmarks, compares them with enrolled student records, and records real-time verified timestamps directly into a structured MySQL database.',
      features: [
        'Real-time webcam video stream capture and frame-by-frame face detection.',
        'High-accuracy facial landmark extraction and biometric matching.',
        'Automated timestamp recording and attendance logging into MySQL.',
        'Proxy attendance mitigation by requiring physical live camera presence.'
      ],
      technologies: ['Python', 'OpenCV', 'Face Recognition', 'MySQL']
    },
    'email-spam': {
      title: 'Email Spam Detection',
      category: 'Machine Learning & NLP',
      overview: 'Built a machine-learning model to classify emails as Spam or Not Spam using email-content analysis and NLP preprocessing.',
      problem: 'The overwhelming volume of spam, phishing, and unwanted promotional emails clutters inboxes and poses significant digital security risks for users and organizations.',
      solution: 'Developed a machine learning classification pipeline with Natural Language Processing (NLP) techniques to analyze message semantics, clean textual features, remove stopwords, and reliably categorize incoming email content as Spam or Ham (Not Spam).',
      features: [
        'NLP preprocessing pipeline including tokenization, lowercasing, and stopword removal.',
        'Text feature extraction and vectorization for numerical machine learning modeling.',
        'Binary classification distinguishing genuine communications from malicious spam.',
        'Rapid inference allowing fast classification of raw email bodies.'
      ],
      technologies: ['Python', 'Machine Learning', 'NLP']
    },
    'captcha-gen': {
      title: 'CAPTCHA Generator',
      category: 'Web Application & Security',
      overview: 'Developed a dynamic CAPTCHA generator to improve web-application security by preventing automated bot scripts.',
      problem: 'Automated bot crawlers, spam bots, and brute-force scripts exploit web forms, skewing analytics and exhausting server resources.',
      solution: 'Engineered a dynamic security verification tool that procedurally generates randomized alphanumeric visual verification codes layered with custom noise patterns, angular distortions, and custom fonts to ensure only human users can submit protected forms.',
      features: [
        'Dynamic procedural generation of randomized alphanumeric security strings.',
        'Custom visual noise overlays and character rotation to defeat OCR bots.',
        'User-friendly frontend verification interface for seamless user confirmation.',
        'Lightweight integration suitable for web application forms and login gates.'
      ],
      technologies: ['Python', 'HTML', 'Web Technologies']
    }
  };

  // Synchronize dynamic projects from Admin Database
  async function syncDynamicProjects() {
    try {
      const res = await fetch('/api/public/projects');
      if (res.ok) {
        const data = await res.json();
        if (data.success && data.projects && data.projects.length > 0) {
          data.projects.forEach(p => {
            PROJECT_DATA[p.slug] = {
              title: p.title,
              category: p.category,
              overview: p.overview,
              problem: p.problem,
              solution: p.solution,
              features: p.features || [],
              technologies: p.technologies || []
            };
          });
        }
      }
    } catch (e) {
      console.info('Using local project baseline.');
    }
  }
  syncDynamicProjects();

  // ==========================================================================
  // 2. DOM Elements Selection
  // ==========================================================================
  const header = document.getElementById('header');
  const scrollProgress = document.getElementById('scroll-progress');
  const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
  const mobileMenu = document.getElementById('mobile-menu');
  const navLinks = document.querySelectorAll('.desktop-nav .nav-link');
  const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');
  const sections = document.querySelectorAll('section[id], header[id]');
  const backToTopBtn = document.getElementById('back-to-top');
  
  // Modals
  const projectModal = document.getElementById('project-modal');
  const modalCloseBtn = document.getElementById('modal-close-btn');
  const modalDismissBtn = document.getElementById('modal-dismiss-btn');
  const modalProjectTitle = document.getElementById('modal-project-title');
  const modalProjectCategory = document.getElementById('modal-project-category');
  const modalProjectBody = document.getElementById('modal-project-body');
  
  const resumeModal = document.getElementById('resume-modal');
  const resumeNavBtn = document.getElementById('resume-nav-btn');
  const resumeCloseBtn = document.getElementById('resume-close-btn');
  const resumeModalTriggers = document.querySelectorAll('.resume-modal-trigger');
  const printResumeBtn = document.getElementById('print-resume-btn');
  
  // Contact Form & Toast
  const contactForm = document.getElementById('portfolio-contact-form');
  const formSuccessBanner = document.getElementById('form-success-banner');
  const toastContainer = document.getElementById('toast-container');

  // ==========================================================================
  // 3. Scroll Progress & Sticky Header
  // ==========================================================================
  const handleScroll = () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    
    // Update progress bar
    if (scrollHeight > 0 && scrollProgress) {
      const progressPercent = (scrollTop / scrollHeight) * 100;
      scrollProgress.style.width = `${progressPercent}%`;
    }

    // Header styling on scroll
    if (header) {
      if (scrollTop > 40) {
        header.classList.add('header-scrolled');
      } else {
        header.classList.remove('header-scrolled');
      }
    }

    // Back to top visibility
    if (backToTopBtn) {
      if (scrollTop > 400) {
        backToTopBtn.classList.add('visible');
      } else {
        backToTopBtn.classList.remove('visible');
      }
    }

    // Scrollspy active link detection
    highlightActiveNavLink(scrollTop);
  };

  window.addEventListener('scroll', handleScroll, { passive: true });

  // Scrollspy helper
  function highlightActiveNavLink(currentScroll) {
    const scrollPosition = currentScroll + 120;
    
    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.offsetHeight;
      const sectionId = section.getAttribute('id');

      if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
        navLinks.forEach(link => {
          link.classList.remove('active');
          if (link.getAttribute('href') === `#${sectionId}`) {
            link.classList.add('active');
          }
        });
      }
    });
  }

  // Back to Top Click
  if (backToTopBtn) {
    backToTopBtn.addEventListener('click', () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }

  // ==========================================================================
  // 4. Mobile Navigation Drawer
  // ==========================================================================
  if (mobileMenuToggle && mobileMenu) {
    const toggleMenu = (open) => {
      const isExpanded = open !== undefined ? open : mobileMenuToggle.getAttribute('aria-expanded') === 'true';
      const newState = !isExpanded;
      
      mobileMenuToggle.setAttribute('aria-expanded', String(newState));
      mobileMenu.setAttribute('aria-hidden', String(!newState));
      
      if (newState) {
        mobileMenu.classList.add('menu-open');
        document.body.style.overflow = 'hidden';
      } else {
        mobileMenu.classList.remove('menu-open');
        document.body.style.overflow = '';
      }
    };

    mobileMenuToggle.addEventListener('click', () => toggleMenu());

    mobileNavLinks.forEach(link => {
      link.addEventListener('click', () => {
        toggleMenu(false);
      });
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
      if (mobileMenu.classList.contains('menu-open') && 
          !mobileMenu.contains(e.target) && 
          !mobileMenuToggle.contains(e.target)) {
        toggleMenu(false);
      }
    });
  }

  // ==========================================================================
  // 5. Scroll Reveal with IntersectionObserver
  // ==========================================================================
  const revealElements = document.querySelectorAll('[data-reveal]');
  
  if ('IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const delay = entry.target.getAttribute('data-delay');
          if (delay) {
            setTimeout(() => {
              entry.target.classList.add('revealed');
            }, parseInt(delay, 10));
          } else {
            entry.target.classList.add('revealed');
          }
          observer.unobserve(entry.target);
        }
      });
    }, {
      root: null,
      threshold: 0.12,
      rootMargin: '0px 0px -40px 0px'
    });

    revealElements.forEach(el => revealObserver.observe(el));
  } else {
    // Fallback if IntersectionObserver is unsupported
    revealElements.forEach(el => el.classList.add('revealed'));
  }

  // ==========================================================================
  // 6. Toast Notification System
  // ==========================================================================
  function showToast(message, type = 'info', duration = 3500) {
    if (!toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Icon based on type
    const iconSvg = type === 'success' 
      ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>'
      : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>';

    toast.innerHTML = `
      ${iconSvg}
      <span>${message}</span>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }

  // ==========================================================================
  // 7. Clipboard Copy Handlers
  // ==========================================================================
  const copyButtons = document.querySelectorAll('.copy-btn');
  copyButtons.forEach(btn => {
    btn.addEventListener('click', async () => {
      const textToCopy = btn.getAttribute('data-copy');
      if (!textToCopy) return;

      try {
        await navigator.clipboard.writeText(textToCopy);
        showToast(`Copied to clipboard: ${textToCopy}`, 'success');
      } catch (err) {
        // Fallback for older browsers
        const tempInput = document.createElement('input');
        tempInput.value = textToCopy;
        document.body.appendChild(tempInput);
        tempInput.select();
        document.execCommand('copy');
        document.body.removeChild(tempInput);
        showToast(`Copied: ${textToCopy}`, 'success');
      }
    });
  });

  // ==========================================================================
  // 8. GitHub / Project Link Placeholders (No Fake URLs)
  // ==========================================================================
  const placeholderButtons = document.querySelectorAll('.github-placeholder-btn');
  placeholderButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const projKey = btn.getAttribute('data-project') || 'project';
      showToast(`Repository: Project source code is available in academic submission and verified repository records.`, 'info', 4500);
    });
  });

  // ==========================================================================
  // 9. Project Case Study Modal
  // ==========================================================================
  const openProjectModal = (projectKey) => {
    const data = PROJECT_DATA[projectKey];
    if (!data || !projectModal) return;

    modalProjectTitle.textContent = data.title;
    modalProjectCategory.textContent = data.category;

    const techChipsHtml = data.technologies
      .map(tech => `<span class="tech-chip">${tech}</span>`)
      .join(' ');

    const featuresHtml = data.features
      .map(feat => `<li>${feat}</li>`)
      .join('');

    modalProjectBody.innerHTML = `
      <div class="modal-case-section">
        <h4 class="modal-case-heading">Project Overview</h4>
        <p class="modal-case-text">${data.overview}</p>
      </div>

      <div class="modal-case-section">
        <h4 class="modal-case-heading">Problem Statement</h4>
        <p class="modal-case-text">${data.problem}</p>
      </div>

      <div class="modal-case-section">
        <h4 class="modal-case-heading">Technical Implementation &amp; Solution</h4>
        <p class="modal-case-text">${data.solution}</p>
      </div>

      <div class="modal-case-section">
        <h4 class="modal-case-heading">Key Features &amp; Capabilities</h4>
        <ul class="modal-case-list">${featuresHtml}</ul>
      </div>

      <div class="modal-case-section">
        <h4 class="modal-case-heading">Technologies Utilized</h4>
        <div class="timeline-tech-stack" style="margin-top: 8px;">${techChipsHtml}</div>
      </div>
    `;

    projectModal.classList.add('modal-active');
    projectModal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  };

  const closeProjectModal = () => {
    if (!projectModal) return;
    projectModal.classList.remove('modal-active');
    projectModal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  };

  document.querySelectorAll('.open-case-study').forEach(btn => {
    btn.addEventListener('click', () => {
      const projKey = btn.getAttribute('data-project');
      openProjectModal(projKey);
    });
  });

  if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeProjectModal);
  if (modalDismissBtn) modalDismissBtn.addEventListener('click', closeProjectModal);
  
  if (projectModal) {
    projectModal.addEventListener('click', (e) => {
      if (e.target === projectModal) closeProjectModal();
    });
  }

  // ==========================================================================
  // 10. Resume Modal Handlers
  // ==========================================================================
  const openResumeModal = () => {
    if (!resumeModal) return;
    resumeModal.classList.add('modal-active');
    resumeModal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  };

  const closeResumeModal = () => {
    if (!resumeModal) return;
    resumeModal.classList.remove('modal-active');
    resumeModal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  };

  if (resumeNavBtn) resumeNavBtn.addEventListener('click', openResumeModal);
  resumeModalTriggers.forEach(btn => btn.addEventListener('click', openResumeModal));
  if (resumeCloseBtn) resumeCloseBtn.addEventListener('click', closeResumeModal);
  
  if (resumeModal) {
    resumeModal.addEventListener('click', (e) => {
      if (e.target === resumeModal) closeResumeModal();
    });
  }

  if (printResumeBtn) {
    printResumeBtn.addEventListener('click', () => {
      window.print();
    });
  }

  // Close modals on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeProjectModal();
      closeResumeModal();
    }
  });

  // ==========================================================================
  // 11. Contact Form Client-Side Validation & Interaction
  // ==========================================================================
  if (contactForm) {
    const nameInput = document.getElementById('form-name');
    const emailInput = document.getElementById('form-email');
    const messageInput = document.getElementById('form-message');
    
    const nameError = document.getElementById('name-error');
    const emailError = document.getElementById('email-error');
    const messageError = document.getElementById('message-error');

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    const validateField = (input, errorEl, condition, msg) => {
      if (!condition) {
        input.classList.add('input-error');
        errorEl.textContent = msg;
        errorEl.classList.add('visible');
        return false;
      } else {
        input.classList.remove('input-error');
        errorEl.classList.remove('visible');
        return true;
      }
    };

    nameInput.addEventListener('input', () => {
      validateField(nameInput, nameError, nameInput.value.trim().length >= 2, 'Please enter your name (at least 2 characters).');
    });

    emailInput.addEventListener('input', () => {
      validateField(emailInput, emailError, emailRegex.test(emailInput.value.trim()), 'Please enter a valid email address.');
    });

    messageInput.addEventListener('input', () => {
      validateField(messageInput, messageError, messageInput.value.trim().length >= 8, 'Please write a message with at least 8 characters.');
    });

    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const isNameValid = validateField(nameInput, nameError, nameInput.value.trim().length >= 2, 'Please enter your name.');
      const isEmailValid = validateField(emailInput, emailError, emailRegex.test(emailInput.value.trim()), 'Please enter a valid email address.');
      const isMessageValid = validateField(messageInput, messageError, messageInput.value.trim().length >= 8, 'Please write a message with at least 8 characters.');

      if (isNameValid && isEmailValid && isMessageValid) {
        const rawName = nameInput.value.trim();
        const rawEmail = emailInput.value.trim();
        const rawMsg = messageInput.value.trim();

        const submitBtn = contactForm.querySelector('button[type="submit"]');
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.textContent = 'Sending...';
        }

        let backendSuccess = false;

        // 1. Try sending directly to the live Flask API Gateway
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 4000);

          const response = await fetch('http://127.0.0.1:5000/api/contact/submit', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              name: rawName,
              email: rawEmail,
              subject: 'Portfolio Inquiry',
              message: rawMsg
            }),
            signal: controller.signal
          });

          clearTimeout(timeoutId);

          if (response.ok) {
            backendSuccess = true;
            showToast('Message sent and recorded successfully to backend database!', 'success', 4500);
          }
        } catch (netErr) {
          console.info('Flask backend offline or unreachable. Using email client fallback.', netErr);
        }

        // 2. Prepare pre-filled Gmail & Mail URLs
        const subjectText = `Portfolio Inquiry from ${rawName}`;
        const bodyText = `Hello Tejaswini,\n\n${rawMsg}\n\n---\nSender Details:\nName: ${rawName}\nEmail: ${rawEmail}`;
        
        const encodedSubject = encodeURIComponent(subjectText);
        const encodedBody = encodeURIComponent(bodyText);

        const gmailComposeUrl = `https://mail.google.com/mail/?view=cm&fs=1&to=pemmasanitejaswini59@gmail.com&su=${encodedSubject}&body=${encodedBody}`;
        const mailtoUrl = `mailto:pemmasanitejaswini59@gmail.com?subject=${encodedSubject}&body=${encodedBody}`;

        // Set action buttons on banner
        const openGmailBtn = document.getElementById('open-gmail-btn');
        if (openGmailBtn) openGmailBtn.href = gmailComposeUrl;

        const openMailAppBtn = document.getElementById('open-mailapp-btn');
        if (openMailAppBtn) openMailAppBtn.href = mailtoUrl;

        // Show success banner UI
        if (formSuccessBanner) {
          formSuccessBanner.style.display = 'flex';
          contactForm.style.display = 'none';
        }

        showToast('Redirecting to your Gmail compose window...', 'success', 4500);

        // 3. Automatically trigger Gmail redirect
        const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
        setTimeout(() => {
          if (isMobile) {
            window.location.href = mailtoUrl;
          } else {
            window.open(gmailComposeUrl, '_blank');
          }
        }, 800);
      } else {
        showToast('Please correct the highlighted form errors before submitting.', 'info');
      }
    });
  }

  // Trigger initial scroll calculation on load
  handleScroll();
});
