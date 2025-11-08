<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>David Arungbemi - AI Engineer & Researcher</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #2563eb;
            --primary-dark: #1e40af;
            --bg: #0f172a;
            --bg-secondary: #1e293b;
            --text: #e2e8f0;
            --text-secondary: #94a3b8;
            --accent: #3b82f6;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }

        /* Navigation */
        nav {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(10px);
            z-index: 1000;
            padding: 1rem 0;
            border-bottom: 1px solid rgba(59, 130, 246, 0.1);
        }

        nav .container {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--accent);
        }

        nav ul {
            display: flex;
            list-style: none;
            gap: 2rem;
        }

        nav a {
            color: var(--text-secondary);
            text-decoration: none;
            transition: color 0.3s;
            font-weight: 500;
        }

        nav a:hover {
            color: var(--accent);
        }

        /* Hero Section */
        .hero {
            min-height: 100vh;
            display: flex;
            align-items: center;
            padding-top: 80px;
        }

        .hero-content {
            max-width: 800px;
        }

        .hero h1 {
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .hero .subtitle {
            font-size: 1.5rem;
            color: var(--text-secondary);
            margin-bottom: 2rem;
        }

        .hero p {
            font-size: 1.1rem;
            color: var(--text-secondary);
            margin-bottom: 2rem;
        }

        .cta-buttons {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .btn {
            padding: 0.875rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
            font-size: 1rem;
        }

        .btn-primary {
            background: var(--primary);
            color: white;
        }

        .btn-primary:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.3);
        }

        .btn-secondary {
            background: transparent;
            color: var(--text);
            border: 2px solid var(--accent);
        }

        .btn-secondary:hover {
            background: var(--accent);
            transform: translateY(-2px);
        }

        /* Section Styling */
        section {
            padding: 5rem 0;
        }

        .section-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 3rem;
            text-align: center;
        }

        /* About Section */
        .about-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
            align-items: center;
        }

        .achievement-card {
            background: var(--bg-secondary);
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            border-left: 4px solid var(--accent);
        }

        .achievement-card h3 {
            color: var(--accent);
            margin-bottom: 0.5rem;
        }

        /* Projects Grid */
        .projects-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
        }

        .project-card {
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 2rem;
            transition: all 0.3s;
            cursor: pointer;
            border: 1px solid rgba(59, 130, 246, 0.1);
        }

        .project-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(59, 130, 246, 0.2);
            border-color: var(--accent);
        }

        .project-card h3 {
            color: var(--accent);
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }

        .project-card p {
            color: var(--text-secondary);
            margin-bottom: 1rem;
        }

        .project-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }

        .tag {
            background: rgba(59, 130, 246, 0.2);
            color: var(--accent);
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
        }

        /* Experience Timeline */
        .timeline {
            position: relative;
            padding-left: 2rem;
        }

        .timeline::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 2px;
            background: var(--accent);
        }

        .timeline-item {
            position: relative;
            margin-bottom: 2rem;
            padding-left: 2rem;
        }

        .timeline-item::before {
            content: '';
            position: absolute;
            left: -2.5rem;
            top: 0;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--accent);
            border: 3px solid var(--bg);
        }

        .timeline-item h3 {
            color: var(--accent);
            margin-bottom: 0.5rem;
        }

        .timeline-item .date {
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }

        /* Publications */
        .publication-card {
            background: var(--bg-secondary);
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            border-left: 4px solid var(--accent);
            transition: all 0.3s;
        }

        .publication-card:hover {
            transform: translateX(10px);
            box-shadow: 0 5px 20px rgba(59, 130, 246, 0.2);
        }

        .publication-card h3 {
            color: var(--text);
            margin-bottom: 0.5rem;
        }

        .publication-card .authors {
            color: var(--text-secondary);
            font-style: italic;
            margin-bottom: 0.5rem;
        }

        /* Contact Section */
        .contact-links {
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
        }

        .contact-card {
            background: var(--bg-secondary);
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            min-width: 200px;
            transition: all 0.3s;
            text-decoration: none;
            color: var(--text);
        }

        .contact-card:hover {
            transform: translateY(-5px);
            background: var(--accent);
        }

        .contact-card svg {
            width: 48px;
            height: 48px;
            margin-bottom: 1rem;
        }

        /* Footer */
        footer {
            background: var(--bg-secondary);
            padding: 2rem 0;
            text-align: center;
            color: var(--text-secondary);
            margin-top: 5rem;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2.5rem;
            }

            .about-content {
                grid-template-columns: 1fr;
            }

            .projects-grid {
                grid-template-columns: 1fr;
            }

            nav ul {
                display: none;
            }

            .cta-buttons {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <nav>
        <div class="container">
            <div class="logo">DA</div>
            <ul>
                <li><a href="#about">About</a></li>
                <li><a href="#projects">Projects</a></li>
                <li><a href="#publications">Publications</a></li>
                <li><a href="#experience">Experience</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </div>
    </nav>

    <section class="hero">
        <div class="container">
            <div class="hero-content">
                <h1>David Adeshina Arungbemi</h1>
                <div class="subtitle">AI Engineer & Researcher</div>
                <p>
                    Co-Founder & Lead AI Engineer at Gyronics. Building the future of gesture-based human-computer interaction 
                    through wearable AI technology. First-class Computer Engineering graduate passionate about 
                    deep learning, interactive systems, and making technology more accessible.
                </p>
                <div class="cta-buttons">
                    <a href="#projects" class="btn btn-primary">View Projects</a>
                    <a href="#contact" class="btn btn-secondary">Get in Touch</a>
                </div>
            </div>
        </div>
    </section>

    <section id="about">
        <div class="container">
            <h2 class="section-title">About Me</h2>
            <div class="about-content">
                <div>
                    <p style="margin-bottom: 1.5rem;">
                        I'm a Computer Engineering graduate from Nile University of Nigeria with a passion for pushing 
                        the boundaries of human-computer interaction through AI and wearable technology.
                    </p>
                    <div class="achievement-card">
                        <h3>🏆 Valedictorian</h3>
                        <p>Best Overall Graduating Student, Nile University of Nigeria (2024)</p>
                    </div>
                    <div class="achievement-card">
                        <h3>🎓 Perfect CGPA</h3>
                        <p>First Class Honours with 5.0/5.0 CGPA in Computer Engineering</p>
                    </div>
                    <div class="achievement-card">
                        <h3>🚀 Startup Winner</h3>
                        <p>Winner of Nile University Startup 4.0 with Gyronics</p>
                    </div>
                </div>
                <div>
                    <h3 style="margin-bottom: 1rem; color: var(--accent);">Skills & Technologies</h3>
                    <div style="margin-bottom: 1.5rem;">
                        <h4 style="color: var(--text); margin-bottom: 0.5rem;">Programming</h4>
                        <div class="project-tags">
                            <span class="tag">Python</span>
                            <span class="tag">C++</span>
                            <span class="tag">TypeScript</span>
                            <span class="tag">Java</span>
                        </div>
                    </div>
                    <div style="margin-bottom: 1.5rem;">
                        <h4 style="color: var(--text); margin-bottom: 0.5rem;">AI & Machine Learning</h4>
                        <div class="project-tags">
                            <span class="tag">TensorFlow</span>
                            <span class="tag">Scikit-learn</span>
                            <span class="tag">NumPy</span>
                            <span class="tag">PyWavelets</span>
                        </div>
                    </div>
                    <div style="margin-bottom: 1.5rem;">
                        <h4 style="color: var(--text); margin-bottom: 0.5rem;">Visualization & Tools</h4>
                        <div class="project-tags">
                            <span class="tag">Matplotlib</span>
                            <span class="tag">Blender</span>
                            <span class="tag">Three.js</span>
                            <span class="tag">LaTeX</span>
                        </div>
                    </div>
                    <div>
                        <h4 style="color: var(--text); margin-bottom: 0.5rem;">Embedded Systems</h4>
                        <div class="project-tags">
                            <span class="tag">Arduino</span>
                            <span class="tag">ESP32</span>
                            <span class="tag">IoT</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section id="projects">
        <div class="container">
            <h2 class="section-title">Featured Projects</h2>
            <div class="projects-grid">
                <div class="project-card" onclick="window.open('https://gyronics.com', '_blank')">
                    <h3>Gyronics Wearable Interface</h3>
                    <p>
                        Co-founded and leading AI development for a revolutionary wearable device that enables 
                        gesture-based control of apps, drones, and devices. End-to-end IMU gesture pipeline with 
                        CNN and attention-based models for real-time gesture recognition.
                    </p>
                    <div class="project-tags">
                        <span class="tag">Deep Learning</span>
                        <span class="tag">IMU Sensors</span>
                        <span class="tag">Real-time Processing</span>
                        <span class="tag">Wearables</span>
                    </div>
                </div>

                <div class="project-card" onclick="window.open('https://ieeexplore.ieee.org/document/11142252', '_blank')">
                    <h3>AI-Based Wearable HCI System</h3>
                    <p>
                        Published research on end-to-end wearable device for real-time gesture recognition of 
                        directional, rotational, and shape-based arm gestures. Featured in IEEE Access journal.
                    </p>
                    <div class="project-tags">
                        <span class="tag">Signal Processing</span>
                        <span class="tag">CNN</span>
                        <span class="tag">Human-Computer Interaction</span>
                        <span class="tag">Research</span>
                    </div>
                </div>

                <div class="project-card" onclick="window.open('https://drive.google.com/drive/folders/1lEC-yjDWrgRX3zha56_j9Smtju4LDh21?usp=sharing', '_blank')">
                    <h3>3D Modeling & Visualization</h3>
                    <p>
                        Collection of 3D models and visualizations created for various projects, including 
                        wearable device prototypes and technical demonstrations using Blender and Three.js.
                    </p>
                    <div class="project-tags">
                        <span class="tag">Blender</span>
                        <span class="tag">Three.js</span>
                        <span class="tag">3D Design</span>
                        <span class="tag">Visualization</span>
                    </div>
                </div>

                <div class="project-card" onclick="window.open('https://github.com/davidAdeshinaArungbemi', '_blank')">
                    <h3>More on GitHub</h3>
                    <p>
                        Explore my other projects including semantic reasoning systems, memory networks, 
                        and various AI experiments on my GitHub profile.
                    </p>
                    <div class="project-tags">
                        <span class="tag">Open Source</span>
                        <span class="tag">AI Research</span>
                        <span class="tag">Experiments</span>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section id="publications">
        <div class="container">
            <h2 class="section-title">Publications</h2>
            <div class="publication-card" onclick="window.open('https://ieeexplore.ieee.org/document/11142252', '_blank')" style="cursor: pointer;">
                <h3>An End to End Wearable Device and System for Real Time Gesture Recognition of Directional, Rotational, and Shape-based Arm Gestures</h3>
                <div class="authors">David A. Arungbemi et al.</div>
                <p style="color: var(--text-secondary);">IEEE Access, 2025</p>
                <p>
                    This paper presents a comprehensive wearable system capable of recognizing complex arm gestures 
                    in real-time, enabling intuitive human-computer interaction without traditional input devices.
                </p>
            </div>
        </div>
    </section>

    <section id="experience">
        <div class="container">
            <h2 class="section-title">Experience</h2>
            <div class="timeline">
                <div class="timeline-item">
                    <h3>Research Intern</h3>
                    <div class="date">National Centre for Artificial Intelligence and Robotics | Feb 2025 - Present</div>
                    <p>
                        Researching integration of object detection, tracking, and classification into live video pipelines. 
                        Developing interactive visualizations and conducting benchmarking studies on model performance.
                    </p>
                </div>

                <div class="timeline-item">
                    <h3>AI Engineer</h3>
                    <div class="date">Gyronics Technologies | Nov 2024 - Present</div>
                    <p>
                        Leading AI development for wearable gesture recognition. Designing CNN and attention-based models, 
                        developing sequence-to-sequence models, and optimizing for real-time deployment.
                    </p>
                </div>

                <div class="timeline-item">
                    <h3>IT Intern</h3>
                    <div class="date">Huawei Technologies Co. Nig. Ltd | March 2023 - Sept 2023</div>
                    <p>
                        Performed server room maintenance, configured enterprise devices, and supported IT infrastructure 
                        operations for a leading technology company.
                    </p>
                </div>
            </div>
        </div>
    </section>

    <section id="contact">
        <div class="container">
            <h2 class="section-title">Get In Touch</h2>
            <div class="contact-links">
                <a href="https://github.com/davidAdeshinaArungbemi" target="_blank" class="contact-card">
                    <svg fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                    <div>GitHub</div>
                </a>

                <a href="https://www.linkedin.com/in/davidadeshina" target="_blank" class="contact-card">
                    <svg fill="currentColor" viewBox="0 0 24 24">
                        <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                    </svg>
                    <div>LinkedIn</div>
                </a>

                <a href="https://gyronics.com" target="_blank" class="contact-card">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/>
                    </svg>
                    <div>Gyronics</div>
                </a>
            </div>
        </div>
    </section>

    <footer>
        <div class="container">
            <p>&copy; 2025 David Adeshina Arungbemi. All rights reserved.</p>
        </div>
    </footer>

    <script>
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    </script>
</body>
</html>
