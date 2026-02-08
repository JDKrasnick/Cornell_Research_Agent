"""Script to populate research interests from extracted data."""

import re
from scraper.sources.data import get_db_connection, update_research_interests

# The extracted research interests data
RESEARCH_DATA = """[1/189] Abe Davis
  URL: https://abedavis.com/
  Publications found: 10
  Success!
  Research areas: computer graphics, computer vision, human-computer interaction, visual vibrometry, computational video editing

[2/189] Aditya Vashistha
  URL: https://www.adityavashistha.com
  Publications found: 1
  Success!
  Research areas: Globally Equitable AI, Human-Computer Interaction, ICT for Development, Human-Centered AI, Social Computing

[3/189] Adrian Lewis
  URL: https://www.duffield.cornell.edu/people/adrian-s-lewis/
  Publications found: 0
  Success!
  Research areas: nonsmooth optimization, variational analysis, computational algorithms, eigenvalue optimization, robust control

[4/189] Adrian Sampson
  URL: https://www.cs.cornell.edu/~asampson/
  Publications found: 1
  Success!
  Research areas: programming languages, computer architecture, approximate computing, hardware-software interface, geometry bugs

[5/189] Ahmed El Alaoui
  URL: https://elalaoui.stat.cornell.edu
  Publications found: 7
  Success!
  Research areas: high-dimensional statistics, probability theory, statistical physics, mean-field spin glasses, random matrix theory

[6/189] Alex Conway
  URL: https://ajhconway.com/
  Publications found: 2
  Success!
  Research areas: randomized data structures, memory systems, storage systems, key-value stores, hash tables

[7/189] Alexander Terenin
  URL: https://avt.im/
  Publications found: 0
  Success!
  Research areas: Bayesian optimization, Gaussian processes, Decision-making under uncertainty, Geometric machine learning, Multi-armed bandits

[8/189] Alexandra Silva
  URL: https://alexandrasilva.org/
  Publications found: 7
  Success!
  Research areas: coalgebra, specification languages, algorithms for models of computation, Kleene Algebra with Tests, verification

[9/189] Allison Koenecke
  URL: https://koenecke.infosci.cornell.edu
  Publications found: 7
  Success!
  Research areas: algorithmic fairness, automated speech recognition, speech-to-text bias, language model fairness, causal inference

[10/189] Andrea Lodi
  URL: https://www.duffield.cornell.edu/people/andrea-lodi/
  Publications found: 0
  Success!
  Research areas: mixed-integer linear programming, mixed-integer nonlinear programming, data science, mathematical optimization, operations research

[11/189] Andreea Minca
  URL: https://people.orie.cornell.edu/acm299/
  Publications found: 0
  Success!
  Research areas: systemic risk, financial networks, financial technologies, stablecoins, central bank digital currency

[12/189] Andrew Chin
  URL: https://www.duffield.cornell.edu/people/andrew-chin/
  Publications found: 0
  Success!
  Research areas: quantitative finance, risk management, portfolio management, quantitative research, asset management

[13/189] Andrew Myers
  URL: https://www.cs.cornell.edu/andru/
  Publications found: 6
  Success!
  Research areas: programming languages, computer security, information flow control, distributed systems, secure computation

[14/189] Andrew Owens
  URL: https://www.andrewowens.com/
  Publications found: 10
  Success!
  Research areas: multimodal learning, self-supervised learning, computer vision, audio-visual learning, tactile sensing

[15/189] Angelina Wang
  URL: https://angelina-wang.github.io/
  Publications found: 3
  Success!
  Research areas: responsible AI, AI fairness, algorithmic fairness, intersectionality, bias measurement

[16/189] Angelique Taylor
  URL: https://www.angeliquemtaylor.com
  Publications found: 10
  Success!
  Research areas: Human-Robot Interaction, Robotics, Computer Vision, Artificial Intelligence, Healthcare Robotics

[17/189] Anil Damle
  URL: https://www.cs.cornell.edu/~damle/
  Publications found: 2
  Success!
  Research areas: Numerical linear algebra, Computational quantum chemistry, Computational statistics, Fast algorithms, Matrix computations

[18/189] Anke van Zuylen
  URL: https://ankevanzuylen.com
  Publications found: 10
  Success!
  Research areas: approximation algorithms, combinatorial optimization, ranking problems, clustering problems, rank aggregation

[19/189] Ari Juels
  URL: http://www.arijuels.com/
  Publications found: 10
  Success!
  Research areas: blockchains, cryptocurrency, smart contracts, applied cryptography, privacy

[20/189] Bart Selman
  URL: https://www.cs.cornell.edu/selman/
  Publications found: 10
  Success!
  Research areas: Artificial Intelligence, Satisfiability (SAT) solving, Model counting, Discrete integration, Constraint satisfaction

[21/189] Bharath Hariharan
  URL: https://www.cs.cornell.edu/~bharathh/
  Publications found: 10
  Success!
  Research areas: computer vision, machine learning, satellite image recognition, earth science applications, vision-language models

[22/189] Brenda Dietrich
  URL: https://www.duffield.cornell.edu/people/brenda-lynn-dietrich/
  Publications found: 0
  Success!
  Research areas: combinatorial duality, mathematical optimization, resource allocation, operations research, data science

[23/189] Bruce Turnbull
  URL: https://people.orie.cornell.edu/bruce/turnbull.html
  Publications found: 0
  Success!
  Research areas: biostatistics, clinical trials, data and safety monitoring, cancer prevention, AIDS prevention

[24/189] Caitlin R. Matthewson
  URL: https://www.duffield.cornell.edu/people/caitlin-matthewson/
  Publications found: 0
  Success!

[25/189] Carla Gomes
  URL: http://www.cs.cornell.edu/gomes
  Publications found: 2
  Success!
  Research areas: Artificial Intelligence, Constraint-based reasoning, Optimization, Machine learning, Computational Sustainability

[26/189] Charles F. Van Loan
  URL: https://www.cs.cornell.edu/cv/
  Publications found: 10
  Success!
  Research areas: Matrix computations, Numerical linear algebra, Matrix exponential, Total least squares, Fast Fourier Transform

[27/189] Cheng Zhang
  URL: https://czhang.org
  Publications found: 10
  Success!
  Research areas: human-centered AI, wearable computing, ubiquitous computing, acoustic sensing, gesture recognition

[28/189] Chris Dawson
  URL: https://www.duffield.cornell.edu/people/chris-dawson/
  Publications found: 0
  Success!

[29/189] Christina Lee Yu
  URL: http://people.orie.cornell.edu/cleeyu/
  Publications found: 13
  Success!
  Research areas: algorithm design and analysis, high dimensional statistics, inference over networks, sequential decision making under uncertainty, online learning

[30/189] Christine Ann Shoemaker
  URL: https://www.duffield.cornell.edu/people/christine-ann-shoemaker/
  Publications found: 0
  Success!
  Research areas: optimization algorithms, global optimization, nonlinear optimization, surrogate response surfaces, high performance computing

[31/189] Christopher De Sa
  URL: https://www.cs.cornell.edu/~cdesa/
  Publications found: 10
  Success!
  Research areas: machine learning systems, neural network quantization, distributed optimization, stochastic gradient descent, low-precision training

[32/189] Claire Cardie
  URL: https://www.cs.cornell.edu/home/cardie/
  Publications found: 10
  Success!
  Research areas: natural language processing, machine learning, neural networks, syntactic analysis, semantic analysis

[33/189] Cornell Jeb E. Brooks School of Public Policy
  URL: https://publicpolicy.cornell.edu/people/moon-duchin/
  Publications found: 0
  Success!
  Research areas: discrete geometry, randomized models, voting and democracy, fair redistricting, gerrymandering

[34/189] Cristian Danescu-Niculescu-Mizil
  URL: https://www.cs.cornell.edu/~cristian/
  Publications found: 1
  Success!
  Research areas: small world graphs, network analysis

[35/189] David Alan Goldberg
  URL: https://people.orie.cornell.edu/dag369/
  Publications found: 0
  Success!
  Research areas: Applied Probability, Stochastic Processes, Queueing Theory, Inventory Models, Optimal Stopping

[36/189] David B. Shmoys
  URL: https://people.orie.cornell.edu/shmoys/
  Publications found: 0
  Success!
  Research areas: approximation algorithms, discrete optimization, linear programming relaxations, NP-hard problems, data-driven models

[37/189] David Bindel
  URL: https://www.cs.cornell.edu/~bindel/
  Publications found: 10
  Success!
  Research areas: numerical analysis, computational science, applied mathematics, stellarator optimization, magnetic confinement fusion

[38/189] David Gries
  URL: http://www.cs.cornell.edu/gries/
  Publications found: 2
  Success!
  Research areas: compiler construction, programming methodology, computer science education, programming languages, formal methods

[39/189] David Mimno
  URL: https://mimno.infosci.cornell.edu
  Publications found: 10
  Success!
  Research areas: topic modeling, large language models, natural language processing, text mining, digital humanities

[40/189] David Ruppert
  URL: https://people.orie.cornell.edu/davidr/
  Publications found: 0
  Success!
  Research areas: Functional data analysis, Nonparametric regression, Statistical machine learning, Measurement error, Bayesian statistics

[41/189] David S. Matteson
  URL: https://davidsmatteson.com
  Publications found: 10
  Success!
  Research areas: Changepoint Detection, High Dimensional Time Series, Functional Data Analysis, Dependence Measures, Varying Parameters

[42/189] David Shmoys
  URL: https://people.orie.cornell.edu/shmoys/
  Publications found: 10
  Success!
  Research areas: approximation algorithms, discrete optimization, linear programming relaxations, NP-hard problems, data-driven models

[43/189] David Williamson
  URL: http://www.davidpwilliamson.net/work
  Publications found: 10
  Success!
  Research areas: Combinatorial Optimization, Approximation Algorithms, Network Design, Facility Location, Scheduling

[44/189] Deborah Estrin
  URL: https://destrin.tech.cornell.edu/
  Publications found: 10
  Success!
  Research areas: digital health, mobile health (mHealth), embedded networked sensing, mobile and wireless systems, federated learning

[45/189] Dexter Kozen
  URL: https://www.cs.cornell.edu/~kozen/
  Publications found: 10
  Success!
  Research areas: logics and semantics of programming languages, algorithms and complexity, decision problems in logic and algebra, probabilistic computation, NetKAT

[46/189] Donald Greenberg
  URL: https://aap.cornell.edu/people/donald-greenberg
  Publications found: 6
  Success!
  Research areas: computer graphics, realistic image synthesis, architectural visualization, rendering algorithms, visual imaging

[47/189] Edward Tom
  URL: https://www.duffield.cornell.edu/people/edward-tom/
  Publications found: 0
  Success!
  Research areas: equity derivatives, quantitative trading strategies, econometric trading algorithms, volatility trading, statistical modeling

[48/189] Eilyan Bitar
  URL: https://bitar.engineering.cornell.edu/
  Publications found: 0
  Success!
  Research areas: robust optimization, stochastic optimization, control theory, game theory, electric power systems

[49/189] Ella Biehn
  URL: https://www.duffield.cornell.edu/people/ella-biehn/
  Publications found: 0
  Success!

[50/189] Eric Lewis Gentsch
  URL: https://www.duffield.cornell.edu/people/eric-lewis-gentsch/
  Publications found: 0
  Success!

[51/189] Eshan Chattopadhyay
  URL: https://www.cs.cornell.edu/~eshan/
  Publications found: 10
  Success!
  Research areas: theoretical computer science, pseudorandomness, randomness extractors, non-malleable codes, computational complexity

[52/189] Fei Shi
  URL: https://www.duffield.cornell.edu/people/fei-shi/
  Publications found: 0
  Success!

[53/189] Fengqi You
  URL: http://peese.org/
  Publications found: 10
  Success!
  Research areas: systems engineering, artificial intelligence, data science, AI for Sustainability (AI4S), AI for Science (AI4Sci)

[54/189] Florentina Bunea
  URL: https://bunea.stat.cornell.edu
  Publications found: 10
  Success!
  Research areas: statistical machine learning theory, high-dimensional statistical inference, soft-max mixtures, LLM/AI algorithms, optimal transport

[55/189] Frans Schalekamp
  URL: http://fransschalekamp.com/
  Publications found: 0
  Success!

[56/189] François Guimbretière
  URL: https://sites.coecis.cornell.edu/fguimbretiere/
  Publications found: 10
  Success!
  Research areas: hardware/software co-design, human-computer interaction, acoustic sensing, wearable computing, hand pose tracking

[57/189] Fred B. Schneider
  URL: https://www.cs.cornell.edu/fbs/
  Publications found: 10
  Success!
  Research areas: cybersecurity, fault-tolerance, distributed systems, concurrent systems, high-integrity systems

[58/189] Gennady Samorodnitsky
  URL: https://people.orie.cornell.edu/gennady/
  Publications found: 0
  Success!
  Research areas: probability theory, stochastic modeling, heavy tails, long-range dependence, financial modeling

[59/189] Giulia Guidi
  URL: https://giuliaguidi.github.io/
  Publications found: 10
  Success!
  Research areas: high-performance computing, parallel computation, sparse linear algebra, computational biology, GPU computing

[60/189] Giuseppe Nuti
  URL: https://www.duffield.cornell.edu/people/giuseppe-nuti/
  Publications found: 0
  Success!
  Research areas: Machine Learning, Artificial Intelligence, Algorithmic Trading, Markov Decision Processes, Financial Computing

[61/189] Greenberg's Cornell AAP profile
  URL: https://aap.cornell.edu/people/donald-greenberg
  Publications found: 0
  Success!
  Research areas: computer graphics, realistic image synthesis, computer graphics in architecture, architectural visualization, visual imaging

[62/189] Greg Morrisett
  URL: http://www.cs.cornell.edu/~jgm/
  Publications found: 10
  Success!
  Research areas: programming languages, type systems, software security, typed assembly language, proof-carrying code

[63/189] Guy Hoffman's Website
  URL: https://hrc2.io/people/guy-hoffman
  Publications found: 0
  Success!
  Research areas: Human-Robot Interaction, Human-Robot Collaboration, Social Robotics, Robotic Companionship, Wearable Robotics

[64/189] Hadar Averbuch-Elor
  URL: https://www.hadarelor.com/
  Publications found: 10
  Success!
  Research areas: computer graphics, computer vision, multimodal perception systems, text-to-image generation, 3D shape manipulation

[65/189] Hakim Weatherspoon
  URL: https://www.cs.cornell.edu/~hweather/
  Publications found: 10
  Success!
  Research areas: distributed systems, cloud computing, networking, digital agriculture, software-defined networking

[66/189] Haym Hirsh
  URL: https://www.cs.cornell.edu/~hirsh/
  Publications found: 10
  Success!
  Research areas: machine learning, data mining, information retrieval, artificial intelligence, text classification

[67/189] Henry Lam
  URL: https://www.duffield.cornell.edu/people/henry-lam/
  Publications found: 0
  Success!

[68/189] Huseyin Topaloglu
  URL: https://people.orie.cornell.edu/huseyin/
  Publications found: 0
  Success!
  Research areas: Revenue Management, Pricing Analytics, Operations Research, Information Engineering, Linear Programming

[69/189] Immanuel Trummer
  URL: https://itrummer.github.io/
  Publications found: 10
  Success!
  Research areas: Database Systems, Large Language Models, Reinforcement Learning, Query Optimization, Database Tuning

[70/189] Irene Ebba Aldridge
  URL: https://www.duffield.cornell.edu/people/irene-ebba-aldridge/
  Publications found: 0
  Success!
  Research areas: market microstructure, high-frequency trading, big data for capital markets, algorithmic trading strategies, quantitative finance

[71/189] Jacob Mays
  URL: https://mays.cee.cornell.edu/
  Publications found: 0
  Success!
  Research areas: stochastic optimization, statistical learning, energy systems, electricity markets, market design

[72/189] James Booth
  URL: https://stat.cornell.edu/people/faculty/james-booth
  Publications found: 0
  Success!
  Research areas: Bootstrap methods, Monte Carlo methods, Clustering, Exact inference, Mixed models

[73/189] James Renegar
  URL: https://math.cornell.edu/james-renegar
  Publications found: 0
  Success!
  Research areas: optimization algorithms, linear programming, linear inequalities, hyperbolic polynomials, polynomial-time algorithms

[74/189] Jamol J. Pender
  URL: https://www.duffield.cornell.edu/people/jamol-j-pender/
  Publications found: 0
  Success!
  Research areas: queueing theory, applied probability, Markov processes, control theory, mathematical finance

[75/189] Jayadev Acharya
  URL: https://people.ece.cornell.edu/acharya/
  Publications found: 3
  Success!
  Research areas: information theory, statistical inference, machine learning, differential privacy, distributed learning

[76/189] Jennifer J. Sun
  URL: https://jenjsun.com/
  Publications found: 10
  Success!
  Research areas: computer vision, machine learning, neurosymbolic programming, self-supervised learning, behavioral video analysis

[77/189] Jessica Rush Leeker
  URL: https://www.duffield.cornell.edu/people/jessica-rush-leeker/
  Publications found: 0
  Success!
  Research areas: Engineering Education, Applied Analytics, Data Science, STEM Accessibility, Data-Driven Decision-Making

[78/189] Jiachang Liu
  URL: https://jiachangliu.github.io/
  Publications found: 0
  Success!
  Research areas: interpretable machine learning, trustworthy AI, human-centered AI, sparse optimization, survival analysis

[79/189] Jim Dai
  URL: https://people.orie.cornell.edu/jdai/
  Publications found: 0
  Success!
  Research areas: Applied Probability, Fluid Models, Diffusion Models, Stochastic Processes, Reinforcement Learning

[80/189] Joachims' Website
  URL: https://www.cs.cornell.edu/people/tj/
  Publications found: 0
  Success!
  Research areas: Machine Learning Methods and Theory, Learning from Human Behavioral Data, Implicit Feedback Learning, Counterfactual Evaluation and Learning, Support Vector Machines

[81/189] Johannes Wissel
  URL: https://www.duffield.cornell.edu/people/johannes-wissel/
  Publications found: 0
  Success!

[82/189] John Anthony Muckstadt
  URL: https://people.orie.cornell.edu/jack/
  Publications found: 0
  Success!
  Research areas: manufacturing systems, manufacturing logistics, supply chain systems, manufacturing system design, manufacturing system analysis

[83/189] John Hopcroft
  URL: https://www.cs.cornell.edu/jeh/
  Publications found: 10
  Success!
  Research areas: theoretical computer science, analysis of algorithms, automata theory, graph algorithms, formal languages

[84/189] John Thickstun
  URL: https://johnthickstun.com/
  Publications found: 10
  Success!
  Research areas: machine learning, generative models, controllable text generation, language models, diffusion models

[85/189] Jon Kleinberg
  URL: https://www.cs.cornell.edu/home/kleinber/
  Publications found: 2
  Success!
  Research areas: algorithms, networks, social networks, information systems, web analysis

[86/189] Joseph Halpern
  URL: https://www.cs.cornell.edu/home/halpern/
  Publications found: 4
  Success!
  Research areas: game theory, decision theory, reasoning about knowledge, reasoning about uncertainty, causality

[87/189] Justin Hsu
  URL: https://www.justinhsu.net/
  Publications found: 7
  Success!
  Research areas: formal verification, probabilistic programming, randomized algorithms, differential privacy, program logics

[88/189] K.-Y. Daisy Fan
  URL: https://www.cs.cornell.edu/~dfan/
  Publications found: 3
  Success!
  Research areas: computer science education, engineering education, collaborative learning methodologies, educational technology, programming pedagogy

[89/189] Karthik Sridharan
  URL: https://www.cs.cornell.edu/~sridharan/
  Publications found: 3
  Success!
  Research areas: theoretical machine learning, machine learning theory, computational learning theory, artificial intelligence, theory of computing

[90/189] Kathryn Caggiano
  URL: https://www.duffield.cornell.edu/people/kathryn-elizabeth-caggiano/
  Publications found: 0
  Success!
  Research areas: Operations Research, Supply Chain Management, Inventory Optimization, Mathematical Modeling, Production Systems

[91/189] Kathryn Zhao
  URL: https://www.duffield.cornell.edu/people/kathryn-zhao/
  Publications found: 0
  Success!
  Research areas: Electronic Trading, Algorithmic Trading, Market Microstructure, Quantitative Research, Portfolio Management

[92/189] Kavita Bala
  URL: https://www.cs.cornell.edu/~kb/
  Publications found: 5
  Success!
  Research areas: computer vision, computer graphics, artificial intelligence, material recognition, visual search and detection

[93/189] Ken Birman
  URL: https://www.cs.cornell.edu/ken/
  Publications found: 2
  Success!
  Research areas: distributed systems, cloud computing, AI/ML systems, edge computing, data movement optimization

[94/189] Kevin Ellis
  URL: https://www.cs.cornell.edu/~ellisk/
  Publications found: 4
  Success!
  Research areas: program synthesis, artificial intelligence, neurosymbolic programming, world models, abstract reasoning

[95/189] Kilian Weinberger
  URL: https://www.cs.cornell.edu/~kilian/
  Publications found: 10
  Success!
  Research areas: machine learning, representation learning, metric learning, deep learning, neural network compression

[96/189] Kristina Monakhova
  URL: https://kristinamonakhova.com/kristina/
  Publications found: 2
  Success!
  Research areas: computational imaging, physics-informed machine learning, lensless imaging, hyperspectral imaging, video denoising

[97/189] Kuan Fang
  URL: https://kuanfang.github.io/
  Publications found: 2
  Success!
  Research areas: robotics, machine learning, computer vision, robot learning, deep learning for robotics

[98/189] Kyra Gan
  URL: https://kyra-gan.github.io/
  Publications found: 9
  Success!
  Research areas: causal discovery, experimental design, statistical inference, precision health, multi-armed bandits

[99/189] Leah Perlmutter
  URL: https://www.cs.cornell.edu/people/leah-perlmutter
  Publications found: 1
  Success!
  Research areas: Human Interaction, Computer Science Education, Student Belonging, Teaching Assistant Interactions, Course Policies

[100/189] Leslie Earl Trotter
  URL: https://www.duffield.cornell.edu/people/leslie-earl-trotter/
  Publications found: 0
  Success!
  Research areas: discrete optimization, combinatorial optimization, stability number, graph theory, abstract duality models

[101/189] Leslie M. Sadler
  URL: https://www.duffield.cornell.edu/people/leslie-m-sadler/
  Publications found: 0
  Success!
  Research areas: academic administration, student affairs, crisis management, COVID-19 response protocols, student support services

[102/189] Lillian Lee
  URL: https://www.cs.cornell.edu/home/llee/
  Publications found: 10
  Success!
  Research areas: Natural Language Processing, Machine Learning, Artificial Intelligence, Social Interaction, Language Technologies

[103/189] Linwei Xin
  URL: https://xin.engineering.cornell.edu
  Publications found: 0
  Success!
  Research areas: inventory management, supply chain management, stochastic inventory theory, asymptotic analysis, deep reinforcement learning

[104/189] Lorenzo Alvisi
  URL: https://www.cs.cornell.edu/lorenzo/
  Publications found: 1
  Success!
  Research areas: distributed computing, dependable systems, fault tolerance, distributed systems theory, distributed computing principles

[105/189] Luiz Vieira
  URL: https://www.duffield.cornell.edu/people/luiz-vieira/
  Publications found: 0
  Success!

[106/189] Malte F. Jung
  URL: https://mjung.infosci.cornell.edu
  Publications found: 10
  Success!
  Research areas: human-robot interaction, group dynamics, team performance, interpersonal dynamics, AI-mediated communication

[107/189] Manxi Wu
  URL: https://sites.google.com/view/manxi-wu/home
  Publications found: 0
  Success!
  Research areas: game theory, multi-agent learning, optimization, urban systems, information design

[108/189] Marcos López de Prado
  URL: https://www.duffield.cornell.edu/people/marcos-lopez-de-prado/
  Publications found: 0
  Success!
  Research areas: financial machine learning, statistical inference, quantitative finance, mathematical finance, financial econometrics

[109/189] Marie Chazal
  URL: https://www.duffield.cornell.edu/people/marie-chazal/
  Publications found: 0
  Success!
  Research areas: mathematical economics, financial mathematics, stochastic processes, option pricing, equilibrium pricing

[110/189] Mark Eisner
  URL: https://www.duffield.cornell.edu/people/mark-eisner/
  Publications found: 0
  Success!

[111/189] Mark Lewis
  URL: https://people.orie.cornell.edu/melewis/
  Publications found: 0
  Success!
  Research areas: Stochastic Processes, Queueing Theory, Markov Decision Processes, Dynamic Resource Allocation, Parallel Processing

[112/189] Martin Wells
  URL: https://scholar.google.com/citations?user=ezjloXIAAAAJ&hl=en
  Publications found: 0
  Success!
  Research areas: Statistics, Biostatistics, Empirical Legal Studies, Epidemiology, Survival Analysis

[113/189] Matthew Eichhorn
  URL: https://maeichho.github.io
  Publications found: 10
  Success!
  Research areas: Causal Inference, Network Interference, Online Algorithms, Mechanism Design, Combinatorics

[114/189] Michael Clarkson
  URL: https://sites.coecis.cornell.edu/clarkson/
  Publications found: 10
  Success!
  Research areas: computer science education, functional programming, OCaml programming, object-oriented programming, formal verification

[115/189] Michael Jeremy Todd
  URL: https://people.orie.cornell.edu/miketodd/todd.html
  Publications found: 0
  Success!
  Research areas: linear programming, convex programming, semidefinite programming, interior-point methods, optimization algorithms

[116/189] Michael Kim
  URL: https://www.cs.cornell.edu/~mpkim/
  Publications found: 2
  Success!
  Research areas: responsible machine learning, algorithmic fairness, machine learning theory, privacy-preserving algorithms, multicalibration

[117/189] Mingming Wang
  URL: https://www.duffield.cornell.edu/people/mingming-wang/
  Publications found: 0
  Success!

[118/189] Moon Duchin
  URL: https://cam.cornell.edu/people/moon-duchin/
  Publications found: 0
  Success!
  Research areas: modeling and mechanism design for electoral systems, networks, geospatial data, demographic data, Markov chains

[119/189] Nancianne Esposito
  URL: https://www.duffield.cornell.edu/people/nancianne-esposito/
  Publications found: 0
  Success!

[120/189] Nate Foster
  URL: https://www.cs.cornell.edu/~jnfoster/
  Publications found: 0
  Success!

[121/189] Nathan Kallus
  URL: https://tech.cornell.edu/people/nathan-kallus
  Publications found: 10
  Success!
  Research areas: causal inference, machine learning, algorithmic fairness, off-policy evaluation, reinforcement learning

[122/189] Nathan Kallus website
  URL: https://tech.cornell.edu/people/nathan-kallus
  Publications found: 0
  Success!
  Research areas: causal inference, machine learning, statistics of optimization under uncertainty, sequential decision making, dynamic decision making

[123/189] Nicholas Spooner
  URL: https://spooner.cc/
  Publications found: 10
  Success!
  Research areas: post-quantum proof systems, probabilistic proof systems, zero knowledge protocols, post-quantum cryptography, quantum information

[124/189] Nicola Dell
  URL: http://www.nixdell.com/
  Publications found: 10
  Success!
  Research areas: human-computer interaction, HCI, information and communication technologies for development, ICTD, computer security

[125/189] Nikhil Garg
  URL: https://gargnikhil.com/
  Publications found: 4
  Success!
  Research areas: public interest AI systems, algorithmic fairness, computational social science, operations research, machine learning

[126/189] Nikita Doikov
  URL: https://doikov.com/
  Publications found: 0
  Error: Failed to fetch page: HTTP 404

[127/189] Noah Snavely
  URL: http://www.cs.cornell.edu/~snavely/
  Publications found: 1
  Success!
  Research areas: computer vision, computer graphics, 3D scene understanding, structure from motion, neural rendering

[128/189] Noah Stephens-Davidowitz
  URL: https://www.noahsd.com/
  Publications found: 10
  Success!
  Research areas: lattices, theoretical computer science, cryptography, geometry, shortest vector problem

[129/189] Omar El Housni
  URL: https://people.orie.cornell.edu/oe46/
  Publications found: 0
  Success!
  Research areas: decision-making under uncertainty, dynamic optimization, robust optimization, revenue management, assortment optimization

[130/189] Onnolee Wierson
  URL: https://www.duffield.cornell.edu/people/onnolee-wierson/
  Publications found: 0
  Success!

[131/189] Owolabi Legunsen
  URL: https://www.cs.cornell.edu/~legunsen/
  Publications found: 10
  Success!
  Research areas: runtime verification, software testing, regression test selection, evolution-aware verification, monitoring-oriented programming

[132/189] Paul Gölz
  URL: https://paulgoelz.de/
  Publications found: 0
  Success!
  Research areas: computational social choice, algorithmic game theory, fair division, citizens' assemblies, sortition

[133/189] Peter  Frazier
  URL: https://people.orie.cornell.edu/pfrazier/
  Publications found: 0
  Success!
  Research areas: AI for Science, Decision making, Preference Learning, Bayesian optimization, Multi-armed bandits

[134/189] Peter Jackson
  URL: http://legacy.orie.cornell.edu/~jackson/new/
  Publications found: 0
  Success!
  Research areas: production planning, scheduling, inventory control, supply chain management, transportation planning

[135/189] Phoebe Sengers
  URL: https://sengers.infosci.cornell.edu
  Publications found: 1
  Success!
  Research areas: Human-Computer Interaction (HCI), Computer-Supported Cooperative Work (CSCW), Science & Technology Studies (STS), Ethnographic analysis, Historical analysis

[136/189] Pierre Patie (on leave)
  URL: https://www.duffield.cornell.edu/people/pierre-patie/
  Publications found: 0
  Success!
  Research areas: stochastic processes, Markov processes, functional analysis, probability theory, financial mathematics

[137/189] Preston Culbertson
  URL: https://pculbertson.github.io
  Publications found: 2
  Success!
  Research areas: robot learning, robustness in robotics, machine learning, numerical optimization, control theory

[138/189] Qian Yang
  URL: https://qianyang.co
  Publications found: 10
  Success!
  Research areas: Human-AI Interaction Design, AI as design material, Responsible AI, Clinical decision support systems, Human-Computer Interaction

[139/189] Raaz Dwivedi
  URL: https://raazdwivedi.github.io/
  Publications found: 0
  Success!
  Research areas: Causal Inference, Distribution Compression, AI Agents for Search, Reinforcement Learning, Kernel Thinning

[140/189] Rachee Singh
  URL: https://www.racheesingh.com/
  Publications found: 0
  Success!
  Research areas: photonic interconnects, distributed machine learning, wide-area networks, traffic engineering, optical networks

[141/189] Rachit Agarwal
  URL: https://www.cs.cornell.edu/~ragarwal/
  Publications found: 10
  Success!
  Research areas: systems, networking, theory, resource disaggregation, host architecture

[142/189] Rafael Pass
  URL: http://www.cs.cornell.edu/~rafael/
  Publications found: 10
  Success!
  Research areas: Blockchain protocols, Consensus mechanisms, Byzantine agreement, Proof of stake, Cryptography

[143/189] Rajalakshmi Nandakumar
  URL: https://infosci.cornell.edu/~rajalakshmi/
  Publications found: 10
  Success!
  Research areas: mobile health, smartphone-based health monitoring, sleep apnea detection, opioid overdose detection, wireless and mobile systems

[144/189] Ramin Zabih
  URL: https://tech.cornell.edu/people/ramin-zabih/
  Publications found: 10
  Success!
  Research areas: computer vision, energy minimization, graph cuts, Markov Random Fields, optical flow

[145/189] Robbert van Renesse
  URL: https://www.cs.cornell.edu/home/rvr/
  Publications found: 10
  Success!
  Research areas: distributed systems, fault tolerance, scalability, state machine replication, replica coordination

[146/189] Robert A. Jarrow
  URL: https://www.johnson.cornell.edu/faculty-and-research/faculty/raj15
  Publications found: 0
  Success!
  Research areas: Mathematical Finance, Derivatives Pricing, Asset Pricing, Risk Management, Heath-Jarrow-Morton Model

[147/189] Robert Bland
  URL: https://people.orie.cornell.edu/bland/
  Publications found: 0
  Success!
  Research areas: Operations Research, Mathematical Optimization, Applied Mathematics

[148/189] Robert Constable
  URL: http://www.cs.cornell.edu/Info/People/rc/
  Publications found: 4
  Success!
  Research areas: automated reasoning, software verification, formal methods, mathematical proofs, program verification

[149/189] Robert Kleinberg
  URL: https://www.cs.cornell.edu/~rdk/
  Publications found: 10
  Success!
  Research areas: multi-armed bandits, algorithmic game theory, online algorithms, mechanism design, machine learning theory

[150/189] Robin  Roundy
  URL: https://www.duffield.cornell.edu/people/robin-roundy/
  Publications found: 0
  Success!
  Research areas: Operations Research, Information Engineering, Mathematics, Optimization

[151/189] Roselle Bajet
  URL: https://www.duffield.cornell.edu/people/roselle-bajet/
  Publications found: 0
  Success!

[152/189] Saikat Dutta
  URL: https://www.cs.cornell.edu/~saikatd/
  Publications found: 10
  Success!
  Research areas: Software Engineering, Machine Learning, Automated Test Generation, ML/DL Library Testing, Probabilistic Programming

[153/189] Sainyam Galhotra
  URL: https://sainyamgalhotra.com/
  Publications found: 10
  Success!
  Research areas: Databases, Data Management, Responsible Data Science, Causal Inference, Machine Learning

[154/189] Samitha Samaranayake
  URL: http://cee.cornell.edu/samitha/
  Publications found: 0
  Success!
  Research areas: mathematical modeling, algorithm design, transportation network problems, public transit, ride-sharing

[155/189] Sanjiban Choudhury
  URL: https://sanjibanc.github.io/
  Publications found: 10
  Success!
  Research areas: reinforcement learning from human feedback, imitation learning, foundation models, robotics, planning

[156/189] Sarah Dean
  URL: https://sdean.website/
  Publications found: 6
  Success!
  Research areas: machine learning, control theory, optimization, dynamical systems, recommendation systems

[157/189] Sasha Stoikov
  URL: http://www.sashastoikov.com/
  Publications found: 0
  Success!
  Research areas: high-frequency trading, music recommendation algorithms, financial engineering, mathematical modeling, data science

[158/189] Shane G. Henderson
  URL: https://people.orie.cornell.edu/shane/
  Publications found: 0
  Success!
  Research areas: Operations Research, Simulation Optimization, Stochastic Simulation, Applied Probability, Emergency Services Planning

[159/189] Shiri Azenkot
  URL: http://shiriazenkot.com/
  Publications found: 10
  Error: Failed to fetch page: HTTP 403

[160/189] Shoham Sabach
  URL: https://www.duffield.cornell.edu/people/shoham-sabach/
  Publications found: 0
  Success!
  Research areas: mathematical optimization, nonconvex optimization, convex bilevel optimization, optimization algorithms, convergence analysis

[161/189] Sid Banerjee
  URL: https://people.orie.cornell.edu/sbanerjee/
  Publications found: 0
  Success!
  Research areas: data-driven decision-making, stochastic control, economics and computation, large-scale network algorithms, online decision-making

[162/189] Sidney Resnick
  URL: https://people.orie.cornell.edu/sid/
  Publications found: 0
  Success!
  Research areas: applied probability, statistics, heavy tails, extreme value theory, regularly varying functions

[163/189] Soroosh Shafiee
  URL: https://www.duffield.cornell.edu/people/soroosh-shafiee/
  Publications found: 0
  Success!
  Research areas: optimization under uncertainty, distributionally robust optimization, optimal transport, low-complexity decision-making, data-driven optimization

[164/189] Steve Marschner
  URL: https://www.cs.cornell.edu/~srm/
  Publications found: 9
  Success!
  Research areas: computer graphics, computer vision, appearance modeling, light scattering, realistic rendering

[165/189] Su Jia
  URL: https://sjia1.github.io/
  Publications found: 0
  Success!
  Research areas: A/B testing, multi-armed bandits, online decision-making, experimental design, interference effects

[166/189] Sumanta Basu
  URL: https://sumbose.stat.cornell.edu
  Publications found: 0
  Success!
  Research areas: statistical machine learning, structure learning, high-dimensional systems, network modeling, time series analysis

[167/189] Tanya Goyal
  URL: https://tagoyal.github.io/
  Publications found: 10
  Success!
  Research areas: Natural Language Processing, Large Language Models, Text Generation Evaluation, Factuality Assessment, Text Summarization

[168/189] Tanzeem Choudhury
  URL: http://www.cs.cornell.edu/~tanzeem/
  Publications found: 10
  Success!
  Research areas: mobile sensing, ubiquitous computing, mental health technology, wearable computing, reality mining

[169/189] Tapomayukh Bhattacharjee
  URL: https://sites.google.com/site/tapomayukh
  Publications found: 10
  Success!
  Research areas: Human-Robot Interaction, Haptic Perception, Robot Manipulation, Assistive Robotics, Activities of Daily Living

[170/189] Thijs Roumen
  URL: https://thijsroumen.eu/
  Publications found: 10
  Success!
  Research areas: digital fabrication, human-computer interaction, laser cutting, 3D modeling, fabrication software tools

[171/189] Thorsten Joachims
  URL: https://www.cs.cornell.edu/people/tj/
  Publications found: 10
  Success!
  Research areas: Machine Learning Methods and Theory, Learning from Human Behavioral Data, Implicit Feedback, Counterfactual Learning and Evaluation, Learning-to-Rank

[172/189] Tim Teitelbaum
  URL: http://www.cs.cornell.edu/info/people/tt/tim_teitelbaum.html
  Publications found: 10
  Success!
  Research areas: Integrated Development Environments, Syntax-Directed Editing, Incremental Computation, Program Synthesizers, Language-Based Editors

[173/189] Tom Ristenpart
  URL: https://rist.tech.cornell.edu/
  Publications found: 10
  Success!
  Research areas: computer security, interpersonal technology abuse, applied cryptography, theoretical cryptography, authentication

[174/189] Troy J. Parish
  URL: https://www.duffield.cornell.edu/people/troy-j-parish/
  Publications found: 0
  Success!

[175/189] Victoria Averbukh
  URL: https://www.duffield.cornell.edu/people/victoria-averbukh/
  Publications found: 0
  Success!
  Research areas: financial modeling, fixed income securities, mortgage-backed securities, quantitative finance, interest-rate securities

[176/189] Vitaly Shmatikov
  URL: http://www.cs.cornell.edu/~shmat/
  Publications found: 2
  Success!

[177/189] Volodymyr Kuleshov
  URL: http://www.cs.cornell.edu/~kuleshov/
  Publications found: 2
  Success!
  Research areas: machine learning, generative models, probabilistic methods, diffusion models, diffusion-based language models

[178/189] Walker White
  URL: https://www.cs.cornell.edu/~wmwhite/
  Publications found: 5
  Success!
  Research areas: data-driven games, database systems, query languages, game design, data stream processing

[179/189] Wei-Chiu Ma
  URL: https://www.cs.cornell.edu/~weichiu/
  Publications found: 3
  Success!
  Research areas: 3D computer vision, 4D computer vision, robotics, neural radiance fields, NeRF

[180/189] Wen Sun
  URL: https://wensun.github.io/
  Publications found: 6
  Success!
  Research areas: Reinforcement Learning, AI, Decision Making, RL for generative models, LLM fine-tuning

[181/189] Wendy Ju
  URL: http://www.wendyju.com/
  Publications found: 1
  Success!
  Research areas: Human-Robot Interaction, Automotive Interaction Design, Interaction with Automation, Interaction Design Research, Implicit Interactions

[182/189] William Arms
  URL: http://www.cs.cornell.edu/wya/
  Publications found: 10
  Success!
  Research areas: Digital Libraries, Academic Computing, Digital Library Architecture, Interoperability, Metadata Systems

[183/189] William Maxwell
  URL: https://www.duffield.cornell.edu/people/william-maxwell/
  Publications found: 0
  Success!
  Research areas: operations research, computer simulation, production planning, scheduling theory, queuing systems

[184/189] Xin Jiang
  URL: https://www.duffield.cornell.edu/people/xin-jiang/
  Publications found: 0
  Success!

[185/189] Yoav Artzi
  URL: http://yoavartzi.com/
  Publications found: 10
  Success!
  Research areas: natural language processing, machine learning, language modeling, continual learning, large language models

[186/189] Yuchen Wu
  URL: https://wuyc0114.github.io/
  Publications found: 0
  Success!
  Research areas: sampling algorithms, Bayesian statistics, diffusion models, computational-statistical tradeoffs, high-dimensional statistics

[187/189] Ziv Goldfeld
  URL: http://people.ece.cornell.edu/zivg/
  Publications found: 10
  Success!
  Research areas: optimal transport theory, Gromov-Wasserstein alignment, information theory, machine learning foundations, mathematical statistics

[188/189] Ziv Scully
  URL: https://ziv.codes/
  Publications found: 0
  Success!
  Research areas: decision-making under uncertainty, stochastic control, queueing theory, scheduling, load balancing

[189/189] Éva Tardos
  URL: https://www.cs.cornell.edu/~eva/
  Publications found: 10
  Success!
  Research areas: algorithmic game theory, mechanism design, auction theory, price of anarchy, smooth mechanisms
"""


def parse_research_data():
    """Parse the research data and extract name -> research areas mapping."""
    entries = {}
    current_entry = {}

    lines = RESEARCH_DATA.strip().split('\n')

    for line in lines:
        line = line.strip()

        # New entry starts with [number/total] Name
        if line.startswith('[') and '/' in line and ']' in line:
            # Save previous entry if it has research areas
            if current_entry.get('name') and current_entry.get('research_areas'):
                entries[current_entry['name']] = current_entry['research_areas']

            # Extract name
            name_match = re.search(r'^\[\d+/\d+\]\s+(.+)$', line)
            if name_match:
                current_entry = {'name': name_match.group(1).strip()}

        # Extract research areas
        elif line.startswith('Research areas:'):
            research_areas = line.replace('Research areas:', '').strip()
            current_entry['research_areas'] = research_areas

    # Don't forget the last entry
    if current_entry.get('name') and current_entry.get('research_areas'):
        entries[current_entry['name']] = current_entry['research_areas']

    return entries


def main():
    """Main function to populate research interests."""
    print("Parsing research data...")
    entries = parse_research_data()
    print(f"Found {len(entries)} faculty members with research interests")

    conn = get_db_connection()

    updated_count = 0
    not_found_count = 0

    print("\nUpdating database...")
    for name, research_interests in entries.items():
        success = update_research_interests(conn, name, research_interests)
        if success:
            updated_count += 1
            print(f"✓ Updated: {name}")
        else:
            not_found_count += 1
            print(f"✗ Not found in DB: {name}")

    conn.close()

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total entries parsed: {len(entries)}")
    print(f"  Successfully updated: {updated_count}")
    print(f"  Not found in database: {not_found_count}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()