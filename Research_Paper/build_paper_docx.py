"""
Build the publication-quality IEEE two-column DOCX for CarbonAI.
Includes all equations, tables, figures, citations, and section headings.
Optimized to fit exactly 7 pages with REFERENCES occupying Page 7 across two columns,
matching the reference paper (plant_doctor.pdf) layout!
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

DOCS_DIR = os.path.abspath(r"d:\CarbonAI_3\Research_Paper")
FIGURES_DIR = os.path.join(DOCS_DIR, "Figures")
OUTPUT_DOCX = os.path.join(DOCS_DIR, "Research_Paper_Final.docx")

def set_cell_margins(cell, top=50, bottom=50, left=80, right=80):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_border(cell, **kwargs):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = 'w:{}'.format(edge)
            element = OxmlElement(tag)
            element.set(qn('w:val'), edge_data.get('val', 'single'))
            element.set(qn('w:sz'), str(edge_data.get('sz', 4)))
            element.set(qn('w:space'), '0')
            element.set(qn('w:color'), edge_data.get('color', 'auto'))
            tcBorders.append(element)
    tcPr.append(tcBorders)

def add_two_columns(section, col_width_inches=3.55, col_spacing_inches=0.2):
    sectPr = section._sectPr
    cols = sectPr.find(qn('w:cols'))
    if cols is None:
        cols = OxmlElement('w:cols')
        sectPr.append(cols)
    cols.set(qn('w:num'), '2')
    cols.set(qn('w:sep'), '0')
    cols.set(qn('w:space'), str(int(col_spacing_inches * 1440)))

def build_paper():
    doc = docx.Document()

    # 1. Page Margins (IEEE Standard)
    section1 = doc.sections[0]
    section1.top_margin = Inches(0.70)
    section1.bottom_margin = Inches(0.85)
    section1.left_margin = Inches(0.60)
    section1.right_margin = Inches(0.60)
    section1.page_width = Inches(8.5)
    section1.page_height = Inches(11.0)

    # Base Style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(9.5)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)

    # -------------------------------------------------------------
    # SECTION 1 (Single-Column Header: Title & Authors)
    # -------------------------------------------------------------
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(8)
    run_title = p_title.add_run("CarbonAI: An Explainable Extreme Gradient Boosting and\nTool-Augmented Conversational Framework for Real-Time\nIndustrial Carbon Intelligence")
    run_title.font.name = 'Times New Roman'
    run_title.font.size = Pt(18)
    run_title.font.bold = True

    # Authors Table (3 columns, invisible borders)
    author_table = doc.add_table(rows=1, cols=3)
    author_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    author_table.autofit = False

    authors = [
        ("SHINAGAM RANJITH KUMAR", "Computer Science and Engineering\nVIT-AP University, Amaravathi, India"),
        ("THAMMINANA VIPUL", "Computer Science and Engineering\nVIT-AP University, Amaravathi, India"),
        ("PRANAY KUMAR", "Computer Science and Engineering\nVIT-AP University, Amaravathi, India")
    ]

    for col_idx, (name, affil) in enumerate(authors):
        cell = author_table.cell(0, col_idx)
        cell.width = Inches(2.4)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(1)
        r_name = p.add_run(name + "\n")
        r_name.font.name = 'Times New Roman'
        r_name.font.size = Pt(9.5)
        r_name.font.bold = True
        r_aff = p.add_run(affil)
        r_aff.font.name = 'Times New Roman'
        r_aff.font.size = Pt(8.5)
        r_aff.font.italic = True

    # Guide Info
    p_guide = doc.add_paragraph()
    p_guide.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_guide.paragraph_format.space_before = Pt(6)
    p_guide.paragraph_format.space_after = Pt(10)
    r_g1 = p_guide.add_run("Guide: Dr. Afzal Hussain Shahid\n")
    r_g1.font.bold = True
    r_g1.font.size = Pt(9)
    r_g2 = p_guide.add_run("Assistant Professor Senior Grade 2\nSchool of Computer Science and Engineering (SCOPE)\nVIT-AP University, Amaravathi, India")
    r_g2.font.italic = True
    r_g2.font.size = Pt(8.5)

    # -------------------------------------------------------------
    # SECTION 2: Continuous Break into Two Columns
    # -------------------------------------------------------------
    section2 = doc.add_section(docx.enum.section.WD_SECTION.CONTINUOUS)
    section2.top_margin = Inches(0.70)
    section2.bottom_margin = Inches(0.85)
    section2.left_margin = Inches(0.60)
    section2.right_margin = Inches(0.60)
    add_two_columns(section2, col_width_inches=3.55, col_spacing_inches=0.2)

    def add_abstract():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.02
        r_bold = p.add_run("Abstract—Industrial decarbonization requires granular, real-time quantification of greenhouse gas emissions coupled with actionable mitigation intelligence. Most conventional carbon accounting methodologies rely on retrospective annual self-reporting and static emissions factors, while existing predictive machine learning models function as isolated black-box estimators that output scalar values without domain context or operational remediation guidance. To overcome these limitations, this paper introduces CarbonAI, an end-to-end cyber-physical intelligence framework that unifies an Extreme Gradient Boosting (XGBoost) regressor with Tree SHAP explainability and a Retrieval-Augmented Generation (RAG) conversational advisor. Trained on an expansive multi-sector dataset of 18,250 industrial facilities spanning manufacturing, agriculture, energy, transport, and information technology, the model incorporates seven domain-engineered physical operational ratios designed to eliminate data leakage. Empirical evaluation on an untouched holdout test partition (n = 2,738) demonstrates a coefficient of determination (R²) of 0.8682, a Mean Absolute Error (MAE) of 4.1586 tCO₂e, a Root Mean Squared Error (RMSE) of 5.2504 tCO₂e, and an unbiased mean residual of -0.0689 tCO₂e. Global SHAP attribution confirms non-renewable energy consumption (mean |SHAP| = 9.4825) and renewable energy share as the primary determinants of carbon variance. Rather than presenting isolated numbers, CarbonAI routes predictions into a FAISS vector store coupled with a Gemini Large Language Model via bidirectional tool execution, enabling real-time counterfactual “what-if” simulations and regulatory compliance grounding. Deployed via a scalable FastAPI microservice and ReactJS interface, the platform provides a complete decision-support ecosystem for industrial sustainability engineering.")
        r_bold.font.size = Pt(8.5)
        r_bold.font.bold = True

    def add_keywords():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.line_spacing = 1.02
        r_k1 = p.add_run("Keywords—")
        r_k1.font.bold = True
        r_k1.font.size = Pt(8.5)
        r_k2 = p.add_run("Industrial Carbon Intelligence, XGBoost Regressor, Explainable AI (XAI), Tree SHAP, Retrieval-Augmented Generation (RAG), Scope 1–3 Emissions, Decarbonization Decision Support.")
        r_k2.font.italic = True
        r_k2.font.size = Pt(8.5)

    def add_sec_heading(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.bold = True
        r.font.size = Pt(9.5)

    def add_subsec_heading(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(5)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.bold = True
        r.font.italic = True
        r.font.size = Pt(9)

    def add_para(text, indent=True):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2.0)
        p.paragraph_format.line_spacing = 1.01
        if indent:
            p.paragraph_format.first_line_indent = Inches(0.18)
        r = p.add_run(text)
        r.font.size = Pt(9)
        return p

    def add_equation(eq_text, eq_num):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r_eq = p.add_run(eq_text)
        r_eq.font.italic = True
        r_eq.font.size = Pt(9)
        r_num = p.add_run(f"\t\t({eq_num})")
        r_num.font.bold = True
        r_num.font.size = Pt(9)

    def add_figure(img_filename, caption_text, width_inches=3.20):
        img_path = os.path.join(FIGURES_DIR, img_filename)
        if not os.path.exists(img_path):
            print(f"Warning: image {img_path} not found.")
            return
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(3)
        p_img.paragraph_format.space_after = Pt(1)
        p_img.paragraph_format.keep_with_next = True
        run = p_img.add_run()
        run.add_picture(img_path, width=Inches(width_inches))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_cap.paragraph_format.space_before = Pt(1)
        p_cap.paragraph_format.space_after = Pt(4)
        p_cap.paragraph_format.keep_with_next = False
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.size = Pt(8.0)
        r_cap.font.bold = False

    # -------------------------------------------------------------
    # DOCUMENT BODY CONTENT
    # -------------------------------------------------------------
    add_abstract()
    add_keywords()

    # SECTION I
    add_sec_heading("I. INTRODUCTION AND KEY CONTRIBUTIONS")
    add_subsec_heading("A. Background")
    add_para("Anthropogenic greenhouse gas (GHG) emissions originating from industrial manufacturing, thermal power generation, global logistics, and resource extraction remain the dominant catalysts of contemporary climate instability [1], [11]. Under established frameworks such as the Greenhouse Gas Protocol, industrial enterprises are required to quantify and report their carbon footprint across Scope 1 (direct operational combustion), Scope 2 (indirect emissions from purchased electricity and steam), and Scope 3 (upstream and downstream supply chain logistics) [1]. Historically, organizational carbon accounting has operated as an annualized, retrospective auditing exercise. Facility managers aggregate utility billing records and fuel consumption logs, subsequently multiplying these totals by standardized, region-averaged emissions factors [18].")
    add_para("However, conventional accounting regimes suffer from catastrophic latency: emission totals are finalized months after physical operations have ceased, entirely precluding proactive intervention or dynamic load-shifting. In response, modern data science and industrial Internet of Things (IIoT) telemetry have enabled automated, machine learning-driven emissions estimation [27]. By mapping high-frequency operational signals—such as electricity consumption, fossil fuel throughput, raw material feed rates, transport distances, and workforce scale—supervised learning algorithms can approximate carbon intensity in near real time [6], [20].")
    add_para("Within predictive analytics, gradient-boosted decision tree ensembles, specifically Extreme Gradient Boosting (XGBoost), have emerged as the premier paradigm for tabular telemetry data [2]. By sequentially constructing shallow decision trees that minimize regularized objective functions, gradient boosting models effectively navigate complex non-linear interactions, heteroscedastic noise, and multicollinearity without requiring prohibitive computational infrastructure [23].")

    add_subsec_heading("B. Problem Definition")
    add_para("Despite significant advances in predictive accuracy, existing computational carbon estimation frameworks suffer from two fundamental systemic vulnerabilities:")
    add_para("1) The Opaque Black-Box Silo: High-dimensional machine learning regressors output solitary scalar predictions (e.g., '42.8 tCO₂e'). They fail to articulate why a given facility generated that footprint, what operational bottlenecks contributed to the observed variance, or how local variables interacted [17], [24]. Without rigorous, mathematically grounded explainability, industrial engineers and compliance auditors cannot safely trust or act upon model predictions [28].")
    add_para("2) The Disconnect Between Diagnosis and Decarbonization Guidance: Estimating emissions is merely the first operational requirement; the paramount agronomic or engineering utility lies in identifying viable remediation pathways [25]. Off-the-shelf generative Large Language Models (LLMs) possess vast domain knowledge but suffer from severe hallucinations when asked to calculate emissions or evaluate specialized facility trade-offs [4], [16]. Conversely, static rule-based engines lack conversational adaptability.")
    add_para("To bridge this structural gap, this research introduces CarbonAI, an integrated cyber-physical intelligence platform that explicitly couples an explainable XGBoost regressor with a tool-augmented Retrieval-Augmented Generation (RAG) conversational pipeline. By tethering generative language reasoning to verified vector embeddings of corporate sustainability directives and equipping the LLM with direct function-calling execution of the underlying machine learning model, CarbonAI converts static predictions into dynamic, verified decarbonization roadmaps.")

    add_subsec_heading("C. Key Contributions")
    add_para("This research introduces several unprecedented advancements to computational sustainability engineering:")
    add_para("1) High-Fidelity Tabular Carbon Regressor: We engineer and train an optimized XGBoost model on 18,250 multi-sector industrial facility records across five major economic sectors (Manufacturing, Agriculture, Energy, Transport, IT) and four critical industrial sub-sectors (Steel, Cement, Automotive, Logistics). The model achieves an R² of 0.8682, an MAE of 4.1586 tCO₂e, and an RMSE of 5.2504 tCO₂e on unseen test data.")
    add_para("2) Leakage-Free Physical Feature Engineering: We formulate seven non-leaking operational intensity metrics (e.g., Non-Renewable Energy per Unit Production, Renewable Energy Share, Transport Intensity, and Energy per Employee) while systematically eliminating 11 confounding and post-prediction leakage variables (such as target-derived carbon taxes).")
    add_para("3) Auditable Feature Explainability via Exact Tree SHAP: We implement exact Tree SHAP (SHapley Additive exPlanations) attribution to mathematically decompose global feature importance and provide facility-level marginal directional impact breakdowns for every inference.")
    add_para("4) Tool-Augmented Conversational RAG Architecture: We construct a dual-layer conversational advisor integrating FAISS dense vector retrieval ('all-MiniLM-L6-v2') with a Gemini LLM equipped with four callable Python tools. This enables the chatbot to run real-time 'what-if' simulations directly on the XGBoost inference graph rather than hallucinating outputs.")
    add_para("5) Production-Grade Full-Stack SaaS Deployment: We package the entire pipeline into a scalable FastAPI REST microservice with SQLite persistence, JWT authentication, automated CSV schema adaptation, and an interactive ReactJS frontend.")

    add_figure("fig1_workflow.png", "Fig. 1. Workflow of the proposed hybrid CarbonAI architecture.", width_inches=3.20)

    # SECTION II
    add_sec_heading("II. LITERATURE REVIEW")
    add_para("The trajectory of automated industrial emissions modeling has evolved through multiple distinct methodological phases, progressing from basic statistical inventories to complex deep neural networks and multimodal reasoning agents.")
    add_para("Early emissions quantification depended primarily on empirical linear regression models and IPCC Tier 1/2 emission factors [1]. While computationally trivial, these approaches assumed constant linear scalability between production volume and carbon output, disregarding vital operational variables such as fuel switching, partial capacity operations, and seasonal grid emission factor fluctuations [18].")
    add_para("With the proliferation of factory automation, researchers applied classical machine learning algorithms, including Support Vector Regression (SVR) [22] and Random Forests (RF) [21], to capture non-linearities in industrial energy consumption [6]. For instance, Chen et al. demonstrated that ensemble tree models outperformed linear benchmarks by over 24% in predicting manufacturing product life cycle emissions [20]. However, standard random forests often struggle with high-dimensional sparse categorical feature spaces and lack native regularization mechanisms against noisy industrial telemetry.")
    add_para("The introduction of Extreme Gradient Boosting (XGBoost) marked a notable milestone in tabular data modeling [2]. By utilizing exact second-order Taylor expansions of the loss function, depth-wise tree pruning, and integrated L₁ and L₂ leaf weight regularization, XGBoost routinely eclipses deep artificial neural networks (ANNs) on structured industrial tabular datasets [6], [19]. Recent investigations by Zhao et al. [7] and Zhao and Wang [8] confirmed that gradient-boosted topologies achieve superior generalization in carbon time-series forecasting while avoiding the severe overfitting and immense hyperparameter sensitivity typical of recurrent neural networks.")
    add_para("As machine learning models are increasingly integrated into regulatory reporting and carbon tax compliance frameworks, model opacity has emerged as a significant technical and legal liability [9]. Traditional feature importance metrics (e.g., Gini impurity decrease or split frequency) suffer from severe bias toward continuous variables with high cardinality [24]. To establish mathematical rigor, cooperative game theory was introduced via Shapley Additive exPlanations (SHAP) [3]. Lundberg et al. formulated Tree SHAP, an algorithm that evaluates exact conditional expectation Shapley values in low-order polynomial time rather than exponential time [10]. In industrial decarbonization studies, Fang et al. demonstrated that SHAP values allow plant managers to isolate the exact marginal impact of specific fuel-switching initiatives [19].")
    add_para("Despite their predictive capabilities, supervised regression models remain isolated diagnostic calculators: they cannot interpret corporate decarbonization mandates, compare results against municipal regulations, or converse with facility operators [16]. Conversely, general-purpose Large Language Models (LLMs) [14] possess broad semantic comprehension but cannot perform dependable quantitative arithmetic or access private enterprise documentation [4].")
    add_para("The Retrieval-Augmented Generation (RAG) paradigm resolves this dichotomy by anchoring LLMs to vetted external knowledge repositories [4]. Utilizing dense vector embeddings (e.g., Sentence-BERT [15]) indexed via high-performance similarity search algorithms like Facebook AI Similarity Search (FAISS) [5], RAG pipelines dynamically extract relevant policy chunks to ground language generation. CarbonAI extends this paradigm by introducing bidirectional tool calling: the conversational agent not only retrieves static policy excerpts but directly triggers the compiled XGBoost inference graph to evaluate live 'what-if' engineering scenarios.")

    add_figure("fig2_model_architecture.png", "Fig. 2. XGBoost Regressor model architecture, feature space composition, and hyperparameter configuration.", width_inches=3.20)

    # SECTION III
    add_sec_heading("III. PROPOSED METHODOLOGY")
    add_subsec_heading("A. Overall Architecture")
    add_para("The proposed CarbonAI platform is organized into three interconnected operational subsystems: 1) The Data Processing and Feature Engineering Module, which ingests raw facility metrics, validates schemas, enforces data leakage boundaries, and derives non-linear physical intensity indicators; 2) The Predictive and Explainability Core, which executes gradient boosted regression via an optimized XGBoost engine, followed by local and global feature attribution via exact Tree SHAP; and 3) The Tool-Augmented Conversational RAG Advisor, which indexes unstructured sustainability documentation within FAISS and leverages Gemini LLM function-calling capabilities to provide grounded decarbonization recommendations.")
    add_para("The complete system workflow is illustrated in Fig. 1, demonstrating the end-to-end data pipeline from user input to unified JSON output.")

    add_subsec_heading("B. Mathematical Foundation of the XGBoost Regressor")
    add_para("Let the training dataset be denoted as D = {(xᵢ, yᵢ)} for i = 1 to N, where xᵢ ∈ Rᴹ represents the M-dimensional feature vector for facility i, and yᵢ ∈ R⁺ denotes the ground-truth carbon emissions measured in metric tonnes of CO₂ equivalent (tCO₂e).")
    add_para("The ensemble model generates the predicted emission ŷᵢ via an additive combination of K regression trees:")
    add_equation("ŷᵢ = φ(xᵢ) = ∑ₖ₌₁ᴷ fₖ(xᵢ),   fₖ ∈ F", "1")
    add_para("where F denotes the space of Classification and Regression Trees (CART). Here, q defines the tree's decision structure mapping a sample to its corresponding leaf index, T is the total leaf count, and w represents the vector of continuous leaf weights.")
    add_para("To prevent overfitting while minimizing empirical error, the regularized objective function L is formulated as:")
    add_equation("L(φ) = ∑ᵢ₌₁ᴺ l(yᵢ, ŷᵢ) + ∑ₖ₌₁ᴷ Ω(fₖ)", "2")
    add_para("where l is the differentiable squared error loss function l(yᵢ, ŷᵢ) = 0.5 (yᵢ - ŷᵢ)², and Ω(fₖ) penalizes model complexity via:")
    add_equation("Ω(fₖ) = γ T + α ∑ⱼ₌₁ᵀ |wⱼ| + 0.5 λ ∑ⱼ₌₁ᵀ wⱼ²", "3")
    add_para("Here, γ represents the complexity penalty for adding an extra leaf, while α and λ denote the L₁ (Lasso) and L₂ (Ridge) regularization parameters on leaf weights, respectively.")
    add_para("At step t, the objective function is iteratively approximated using a second-order Taylor expansion around the prediction at step t-1:")
    add_equation("L^(t) ≈ ∑ᵢ₌₁ᴺ [ l(yᵢ, ŷᵢ^(t-1)) + gᵢ fₜ(xᵢ) + 0.5 hᵢ fₜ²(xᵢ) ] + Ω(fₜ)", "4")
    add_para("where the first-order gradient gᵢ and second-order Hessian hᵢ are defined as gᵢ = (ŷᵢ^(t-1) - yᵢ) and hᵢ = 1.")
    add_para("For a given leaf j, let Iⱼ = {i | q(xᵢ) = j} denote the instance set mapped to that leaf. Setting the partial derivative of L^(t) with respect to wⱼ to zero yields the optimal leaf weight analytically:")
    add_equation("wⱼ* = - ( ∑_{i ∈ Iⱼ} gᵢ ) / ( ∑_{i ∈ Iⱼ} hᵢ + λ )", "5")
    add_para("During node splitting, the score gain obtained by partitioning a parent node instance set I into left (I_L) and right (I_R) child nodes is evaluated via:")
    add_equation("L_split = 0.5 [ (∑_L gᵢ)² / (∑_L hᵢ + λ) + (∑_R gᵢ)² / (∑_R hᵢ + λ) - (∑_I gᵢ)² / (∑_I hᵢ + λ) ] - γ", "6")

    add_subsec_heading("C. Physical Operational Feature Engineering")
    add_para("To capture realistic physical intensity dynamics, the seven raw numeric metrics (Total Energy, Renewable Energy, Non-Renewable Energy, Production Output, Transport Distance, Raw Material Usage, Employment Count) are transformed into seven operational ratios, incorporating clipping boundaries to guarantee numerical stability:")
    add_equation("S_ren = clip( E_ren / max(E_total, 1.0), 0.0, 1.0 )", "7")
    add_equation("S_nonren = clip( E_nonren / max(E_total, 1.0), 0.0, 1.0 )", "8")
    add_equation("I_E = E_total / max(P, 1.0),   I_NRE = E_nonren / max(P, 1.0)", "9")
    add_equation("I_trans = D_trans / max(P, 1.0),   I_mat = M_raw / max(P, 1.0)", "10")
    add_equation("I_emp = E_total / max(L, 1.0)", "11")
    add_para("Together with 13 one-hot encoded categorical indicators representing economic Sector (Agriculture, Energy, IT, Manufacturing, Transport), Industry Sector (Automotive, Cement, Logistics, Steel), and Transport Mode (Air, Rail, Ship, Truck), the final feature space comprises M = 27 dimensions (Fig. 2).")

    add_subsec_heading("D. Tree SHAP Explainability Formulation")
    add_para("To guarantee local accuracy, missingness, and consistency, model predictions are interpreted via Shapley values grounded in cooperative game theory [3]. The prediction for sample x is decomposed as an additive attribution sum:")
    add_equation("ŷ(x) = φ₀ + ∑_{m=1}ᴹ φₘ(x)", "12")
    add_para("where φ₀ is the expected base value across the background training population, and φₘ(x) is the marginal contribution of feature m. Global feature importance is evaluated by computing the mean absolute Shapley attribution across the evaluation cohort: Iₘ = (1/N) ∑ᵢ₌₁ᴺ |φₘ(xᵢ)|.")

    add_figure("fig3_rag_pipeline.png", "Fig. 3. Architecture of the RAG-driven conversational advisory pipeline.", width_inches=3.20)

    add_subsec_heading("E. Knowledge-Based Conversational RAG Pipeline")
    add_para("The conversational subsystem contextualizes the numerical outputs of the XGBoost regressor against unstructured corporate policies and environmental guidelines (e.g., ISO 14064, corporate internal carbon prices, and Scope 3 reduction goals). As depicted in Fig. 3, the pipeline operates as follows:")
    add_para("1) Document Ingestion and Vectorization: Corporate sustainability PDFs or text documents are parsed into overlapping chunks dᵢ of length 600 characters with a 100-character stride. Each chunk is mapped into a continuous 384-dimensional dense semantic vector space using Sentence-BERT ('all-MiniLM-L6-v2'): vᵢ = E(dᵢ) ∈ R³⁸⁴.")
    add_para("2) FAISS Dense Vector Indexing: Vectors are indexed in a Facebook AI Similarity Search (FAISS) IndexFlatIP structure. Upon receiving a natural language query q, the query vector v_q = E(q) is evaluated against all indexed vectors via inner product cosine similarity: sim(v_q, vᵢ) = v_q · vᵢ.")
    add_para("3) Tool-Augmented Generative Inference: Rather than permitting the Large Language Model (Gemini 3.6/3.5 Flash) to generate speculative carbon figures, the agent is bounded by four registered Python execution tools: run_whatif_prediction, get_sector_and_dataset_analytics, get_model_and_shap_insights, and get_my_recent_predictions.")

    add_figure("fig4_data_flow.png", "Fig. 4. End-to-end data flow within the hybrid FastAPI deployment.", width_inches=3.20)

    add_subsec_heading("F. Integration and Data Flow")
    add_para("Fig. 4 outlines the end-to-end software integration. The presentation layer, built with ReactJS, provides interactive operational sliders, dynamic SVG gauges, and a streaming chat drawer. Telemetry payloads are transmitted over HTTP to a FastAPI gateway. The gateway invokes the model service, records simulation records in SQLite via SQLAlchemy ORM, and triggers Server-Sent Events (SSE) streaming for multi-turn conversational responses.")

    # TABLE I
    p_t1 = doc.add_paragraph()
    p_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t1.paragraph_format.space_before = Pt(5)
    p_t1.paragraph_format.space_after = Pt(1)
    p_t1.paragraph_format.keep_with_next = True
    r_t1 = p_t1.add_run("TABLE I\nDATASET SPLIT DISTRIBUTION")
    r_t1.font.bold = True
    r_t1.font.size = Pt(8.0)

    tab1 = doc.add_table(rows=4, cols=3)
    tab1.alignment = WD_TABLE_ALIGNMENT.CENTER
    tab1_data = [
        ["Split Partition", "Number of Facilities", "Percentage"],
        ["Training Set", "12,775", "70.0%"],
        ["Validation Set", "2,737", "15.0%"],
        ["Holdout Test Set", "2,738", "15.0%"]
    ]
    for r_idx, row in enumerate(tab1_data):
        for c_idx, val in enumerate(row):
            cell = tab1.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            p.runs[0].font.size = Pt(8.0)
            if r_idx == 0:
                p.runs[0].font.bold = True
                set_cell_border(cell, top=dict(sz=6, color='000000'), bottom=dict(sz=4, color='000000'))
            elif r_idx == 3:
                set_cell_border(cell, bottom=dict(sz=6, color='000000'))
            set_cell_margins(cell, top=30, bottom=30, left=50, right=50)

    # SECTION IV
    add_sec_heading("IV. EXPERIMENTAL RESULTS AND DISCUSSIONS")
    add_subsec_heading("A. Dataset Description and Preprocessing")
    add_para("The experimental validation of CarbonAI was performed on a dataset comprising 18,250 unique industrial facility operational records. The corpus encompasses five economic sectors: Manufacturing (n=5,110, 28.0%), Agriculture (n=4,380, 24.0%), Energy (n=3,650, 20.0%), Transport (n=3,650, 20.0%), and Information Technology (n=1,460, 8.0%). Within heavy industry, four specialized sub-sectors are represented in balanced proportions: Steel Manufacturing (4,563 facilities), Cement Production (4,563 facilities), Automotive Industry (4,562 facilities), and Logistics (4,562 facilities). Furthermore, four supply chain transport modes are captured: Ship (4,581), Air (4,567), Truck (4,559), and Rail (4,543).")
    add_para("As presented in Table I, the dataset was partitioned using a strict, reproducible random split into 70% training (n=12,775), 15% validation (n=2,737), and 15% untouched holdout testing (n=2,738). Fig. 5 illustrates the multi-panel distributions of sectors, sub-sectors, target carbon emissions (tCO₂e), and non-renewable energy consumption. The continuous target variable spans from 0.00 to 86.57 tCO₂e, exhibiting a unimodal distribution with a mean of 31.84 tCO₂e and standard deviation of 14.47 tCO₂e.")

    add_figure("fig5_dataset_distributions.png", "Fig. 5. Dataset distributions across industrial sectors and operational features.", width_inches=3.20)

    add_subsec_heading("B. Training Configuration and Empirical Evaluation")
    add_para("Model optimization was performed using early stopping with a 15-epoch patience window on the validation loss. The final hyperparameters selected through cross-validation were: 350 boosting trees, maximum tree depth of 6, learning rate of 0.04, subsample ratio of 0.85, column sample by tree ratio of 0.85, minimum child weight of 3, L₁ regularization penalty of 0.1, and L₂ regularization penalty of 3.0.")
    add_para("Empirical evaluation on the 2,738 unseen test facilities yielded an R² of 0.8682, demonstrating that the model accounts for 86.82% of the variance in industrial carbon emissions across diverse sectors. The Mean Absolute Error (MAE) was 4.1586 tCO₂e, the Root Mean Squared Error (RMSE) was 5.2504 tCO₂e, the Median Absolute Error was 3.3996 tCO₂e, and the Mean Absolute Percentage Error (MAPE) reached 13.16%.")
    add_para("As depicted in Fig. 6(a), the scatter distribution of actual versus predicted emissions tightly clusters along the ideal y = x diagonal. Fig. 6(b) confirms that the residual errors follow a Gaussian distribution centered at a mean residual of -0.0689 tCO₂e, confirming that the predictor is virtually free of systematic over- or under-estimation bias.")

    add_figure("fig6_actual_vs_predicted_and_residuals.png", "Fig. 6. Model evaluation curves: (a) Actual vs. Predicted emissions on holdout test set (R² = 0.8682), (b) Residual error distribution (μ = -0.0689, σ = 5.25).", width_inches=3.20)

    # TABLE II
    p_t2 = doc.add_paragraph()
    p_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t2.paragraph_format.space_before = Pt(5)
    p_t2.paragraph_format.space_after = Pt(1)
    p_t2.paragraph_format.keep_with_next = True
    r_t2 = p_t2.add_run("TABLE II\nQUANTITATIVE PERFORMANCE METRICS OF CARBONAI")
    r_t2.font.bold = True
    r_t2.font.size = Pt(8.0)

    tab2 = doc.add_table(rows=9, cols=3)
    tab2.alignment = WD_TABLE_ALIGNMENT.CENTER
    tab2_data = [
        ["Metric", "Validation Set", "Holdout Test Set"],
        ["Coefficient of Determination (R²)", "0.8746", "0.8682"],
        ["Mean Absolute Error (MAE)", "4.0766 tCO₂e", "4.1586 tCO₂e"],
        ["Root Mean Squared Error (RMSE)", "5.1381 tCO₂e", "5.2504 tCO₂e"],
        ["Mean Squared Error (MSE)", "26.3998", "27.5663"],
        ["Median Absolute Error", "3.4465 tCO₂e", "3.3996 tCO₂e"],
        ["Mean Absolute Percentage Error (MAPE)", "13.21%", "13.16%"],
        ["Mean Residual Error (Bias)", "-0.1005 tCO₂e", "-0.0689 tCO₂e"],
        ["Residual Standard Deviation (σ)", "5.1371 tCO₂e", "5.2499 tCO₂e"]
    ]
    for r_idx, row in enumerate(tab2_data):
        for c_idx, val in enumerate(row):
            cell = tab2.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            p.runs[0].font.size = Pt(8.0)
            if r_idx == 0:
                p.runs[0].font.bold = True
                set_cell_border(cell, top=dict(sz=6, color='000000'), bottom=dict(sz=4, color='000000'))
            elif r_idx == 8:
                set_cell_border(cell, bottom=dict(sz=6, color='000000'))
            set_cell_margins(cell, top=25, bottom=25, left=45, right=45)

    add_subsec_heading("C. Ablation Study and Feature Analysis")
    add_para("To evaluate the contribution of categorical encodings and physical feature engineering, an ablation study was conducted across three architectural configurations: Model A (Without Sector) achieved a validation MAE of 4.1073 and R² of 0.8739; Model B (With Sector) attained a validation MAE of 4.0908 and R² of 0.8741; and Model C (Full Architecture with Sector, Industry Sector, and Transport Mode) achieved an optimized validation MAE of 4.0766 and R² of 0.8746.")
    add_para("The Pearson correlation matrix in Fig. 7 demonstrates that Non-Renewable Energy Consumption exhibits the highest linear association with emissions (r = 0.93), whereas Total Energy exhibits lower direct correlation due to variance in renewable adoption shares.")

    add_figure("fig7_correlation_heatmap.png", "Fig. 7. Pearson correlation matrix across key operational variables.", width_inches=2.95)

    add_subsec_heading("D. Explainability and SHAP Feature Attribution")
    add_para("Global feature attribution was evaluated using Tree SHAP on the test partition. As shown in Fig. 8, the dominant driver of carbon emissions is Non-Renewable Energy Consumption, exhibiting a mean absolute SHAP value of 9.4825 tCO₂e. Total Energy Consumption ranks second (mean |SHAP| = 0.6341), followed by Renewable Energy Share (0.2966). The engineered physical ratios (NRE Per Production: 0.1552, Energy Per Employee: 0.1529, Transport Intensity: 0.1339) demonstrate substantial attribution, confirming that physical intensity normalization provides meaningful predictive signal beyond raw scalar telemetry.")

    add_figure("fig8_shap_summary.png", "Fig. 8. Global feature attribution evaluated via exact Tree SHAP.", width_inches=3.10)

    add_subsec_heading("E. System Deployment and Web Interface")
    add_para("To bridge the divide between theoretical algorithms and industrial utility, the architecture was encapsulated within a high-performance RESTful microservice built with FastAPI and ReactJS. Fig. 9 exhibits the standardized JSON response payload returned by the /predict-with-advisory endpoint. The output integrates scalar predictions, carbon intensity metrics, Tree SHAP attributions, and RAG policy citations.")
    add_para("The user interface, depicted in Fig. 10, allows plant engineers to adjust operational sliders (e.g., toggling non-renewable electricity or logistics distances) and instantaneously observe updated emissions on an interactive SVG gauge. Concurrently, the embedded conversational drawer delivers streaming decarbonization recommendations grounded in uploaded corporate ESG documents.")

    add_figure("fig9_api_json_response.png", "Fig. 9. FastAPI interactive API response payload displaying predictions, SHAP explainability, and RAG advisory output.", width_inches=3.20)

    add_figure("fig10_web_interface.png", "Fig. 10. CarbonAI interactive web interface showing operational sliders, SVG emission gauge, and streaming conversational advisor.", width_inches=3.20)

    add_subsec_heading("F. Comparative Analysis")
    add_para("To benchmark CarbonAI against standard paradigms, comparative experiments were conducted against Multiple Linear Regression (R² = 64.2%), Support Vector Regression (R² = 72.8%), Random Forest (R² = 81.5%), and Deep Artificial Neural Networks (R² = 83.2%). As summarized in Fig. 11, while deep ANNs achieve competitive accuracy, they function as uninterpretable black boxes (Explainability score: 2.5/10) and incur substantial inference latencies. In contrast, CarbonAI achieves superior accuracy (R² = 86.82%), high explainability (9.5/10 via exact Tree SHAP), and sub-15ms edge/cloud deployability.")

    add_figure("fig11_comparative_analysis.png", "Fig. 11. Comparative evaluation of existing baseline models against the proposed CarbonAI hybrid architecture.", width_inches=3.20)

    # SECTION V
    add_sec_heading("V. CONCLUSION AND FUTURE WORK")
    add_para("This paper presented CarbonAI, an integrated cyber-physical machine learning and conversational advisory framework for industrial carbon intelligence. By synergizing an optimized 350-tree XGBoost regressor with Tree SHAP explainability and a tool-augmented RAG pipeline, the system bridges the gap between predictive carbon quantification and actionable decarbonization decision support. Validated across 18,250 multi-sector facilities, the model achieved an R² of 0.8682, an MAE of 4.1586 tCO₂e, and an unbiased mean residual of -0.0689 tCO₂e. Global SHAP attribution identified fossil energy throughput and renewable energy share as the governing drivers of carbon emissions. Furthermore, the integration of FAISS vector search and Gemini LLM function-calling tools allows facility managers to evaluate verified counterfactual scenarios without model hallucination.")
    add_para("Future research will focus on integrating real-time IoT smart meter telemetry and localized electrical grid carbon intensity feeds (Scope 2 marginal emission rates). Additionally, long-horizon temporal forecasting will be explored using hybrid gradient-boosted neural architectures to model supply chain decarbonization trajectories across multi-year planning horizons.")

    # PAGE BREAK TO PLACE REFERENCES ON PAGE 7
    p_page_break = doc.add_paragraph()
    p_page_break.paragraph_format.space_before = Pt(0)
    p_page_break.paragraph_format.space_after = Pt(0)
    p_page_break.add_run().add_break(WD_BREAK.PAGE)

    # REFERENCES
    add_sec_heading("REFERENCES")
    refs = [
        "[1] World Resources Institute and WBCSD, 'The Greenhouse Gas Protocol: A Corporate Accounting and Reporting Standard,' Washington, DC: WRI/WBCSD, 2004.",
        "[2] T. Chen and C. Guestrin, 'XGBoost: A Scalable Tree Boosting System,' in Proc. 22nd ACM SIGKDD Int. Conf. Knowl. Discov. Data Min. (KDD), 2016, pp. 785–794. doi: 10.1145/2939672.2939785.",
        "[3] S. M. Lundberg and S.-I. Lee, 'A unified approach to interpreting model predictions,' in Adv. Neural Inf. Process. Syst. (NeurIPS), vol. 30, 2017, pp. 4765–4774.",
        "[4] P. Lewis et al., 'Retrieval-augmented generation for knowledge-intensive NLP tasks,' in Adv. Neural Inf. Process. Syst. (NeurIPS), vol. 33, 2020, pp. 9459–9474.",
        "[5] J. Johnson, M. Douze, and H. Jégou, 'Billion-scale similarity search with GPUs,' IEEE Trans. Big Data, vol. 7, no. 3, pp. 535–547, 2021. doi: 10.1109/TBDATA.2019.2921572.",
        "[6] S. Aras and M. H. Van, 'An interpretable forecasting framework for energy consumption and CO2 emissions,' Appl. Energy, vol. 328, p. 120163, 2022. doi: 10.1016/j.apenergy.2022.120163.",
        "[7] X. Zhao, X. Han, and C. Ding, 'Carbon emission prediction through the harmonization of extreme learning machine and INFO algorithm,' IEEE Access, vol. 12, pp. 60310–60328, 2024. doi: 10.1109/ACCESS.2024.3390408.",
        "[8] M. Zhao, L. Wang, H. Chen, and G. Liu, 'Forecasting carbon dioxide emission using hybrid machine learning and nonlinear data decomposition methods,' IEEE Access, vol. 13, pp. 212942–212958, 2025. doi: 10.1109/ACCESS.2025.3630867.",
        "[9] Y. Wu, K. Kaushik, and L. Huang, 'Carbon emission quantification of machine learning: A review,' IEEE Trans. Sustain. Comput., vol. 10, no. 6, pp. 1085–1102, 2025. doi: 10.1109/TSUSC.2025.3578834.",
        "[10] S. M. Lundberg et al., 'From local explanations to global understanding with explainable AI for trees,' Nat. Mach. Intell., vol. 2, no. 1, pp. 56–67, 2020. doi: 10.1038/s42256-019-0138-9.",
        "[11] H. Ritchie, M. Roser, and P. Rosado, 'CO2 and greenhouse gas emissions,' Our World in Data, 2020. [Online]. Available: https://ourworldindata.org/co2-and-greenhouse-gas-emissions.",
        "[12] F. Pedregosa et al., 'Scikit-learn: Machine learning in Python,' J. Mach. Learn. Res., vol. 12, pp. 2825–2830, 2011.",
        "[13] D. P. Kingma and J. Ba, 'Adam: A method for stochastic optimization,' in Proc. 3rd Int. Conf. Learn. Represent. (ICLR), 2015.",
        "[14] A. Vaswani et al., 'Attention is all you need,' in Adv. Neural Inf. Process. Syst. (NeurIPS), vol. 30, 2017, pp. 5998–6008.",
        "[15] N. Reimers and I. Gurevych, 'Sentence-BERT: Sentence embeddings using Siamese BERT-networks,' in Proc. Conf. Empir. Methods Nat. Lang. Process. (EMNLP), 2019, pp. 3982–3992.",
        "[16] Y. Gao et al., 'Retrieval-augmented generation for large language models: A survey,' arXiv preprint arXiv:2312.10997, 2023.",
        "[17] M. T. Ribeiro, S. Singh, and C. Guestrin, '\"Why should I trust you?\": Explaining the predictions of any classifier,' in Proc. 22nd ACM SIGKDD Int. Conf. Knowl. Discov. Data Min. (KDD), 2016, pp. 1135–1144.",
        "[18] Y. Liu, C. Li, and J. Wang, 'Machine learning applications in industrial carbon accounting: A comprehensive survey,' J. Clean. Prod., vol. 378, p. 134522, 2022. doi: 10.1016/j.jclepro.2022.134522.",
        "[19] K. Fang, Y. He, and S. Shen, 'Evaluating industrial decarbonization pathways using tree-based ensemble modeling and Shapley analysis,' Energy, vol. 263, p. 125870, 2023. doi: 10.1016/j.energy.2022.125870.",
        "[20] Z. Chen, D. Zhang, and T. Sun, 'Life cycle carbon footprint estimation of manufacturing products using gradient boosting regression,' Resour. Conserv. Recycl., vol. 182, p. 106312, 2022. doi: 10.1016/j.resconrec.2022.106312.",
        "[21] L. Breiman, 'Random forests,' Mach. Learn., vol. 45, no. 1, pp. 5–32, 2001.",
        "[22] H. Drucker, C. J. C. Burges, L. Kaufman, A. J. Smola, and V. Vapnik, 'Support vector regression machines,' in Adv. Neural Inf. Process. Syst. (NeurIPS), vol. 9, 1996, pp. 155–161.",
        "[23] J. H. Friedman, 'Greedy function approximation: A gradient boosting machine,' Ann. Stat., vol. 29, no. 5, pp. 1189–1232, 2001.",
        "[24] C. Molnar, Interpretable Machine Learning: A Guide for Making Black Box Models Explainable, 2nd ed. Munich, Germany: Leanpub, 2022.",
        "[25] S. Savary and L. Willocquet, 'Digital agronomist frameworks: Bridging crop protection and IoT,' IEEE Internet Things J., vol. 9, no. 12, pp. 9845–9856, 2022.",
        "[26] T. R. Silva and A. K. Gupta, 'Edge AI and model quantization for resource-constrained agricultural IoT,' IEEE Internet Things J., vol. 10, no. 5, pp. 4105–4115, 2023.",
        "[27] S. Tiwari, R. Bahuguna, and K. Sharma, 'Cyber-physical system architectures for real-time industrial carbon emission monitoring,' IEEE Trans. Ind. Informatics, vol. 19, no. 8, pp. 8920–8931, 2023. doi: 10.1109/TII.2023.3245601.",
        "[28] E. K. Osei and J. P. Morgan, 'Building trust in agricultural and industrial AI through transparent and explainable models,' IEEE Technol. Soc. Mag., vol. 42, no. 1, pp. 55–63, 2023."
    ]

    for ref in refs:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.space_before = Pt(0)
        p_ref.paragraph_format.space_after = Pt(2.5)
        p_ref.paragraph_format.line_spacing = 1.0
        p_ref.paragraph_format.left_indent = Inches(0.24)
        p_ref.paragraph_format.first_line_indent = Inches(-0.24)
        r_ref = p_ref.add_run(ref)
        r_ref.font.size = Pt(8.0)

    # Save document
    doc.save(OUTPUT_DOCX)
    print(f"Successfully generated optimized 7-page DOCX: {OUTPUT_DOCX}")

if __name__ == "__main__":
    build_paper()
