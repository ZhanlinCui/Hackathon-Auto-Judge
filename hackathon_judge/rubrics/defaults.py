DEFAULT_RUBRICS = [
    {
        "dimension": "technical",
        "name": "Technical Soundness",
        "weight": 0.30,
        "criteria": (
            "Evaluate the technical quality of this hackathon project. "
            "Consider code architecture, use of appropriate technologies, "
            "error handling, code organization, and engineering best practices."
        ),
        "evaluation_steps": [
            "Review the project's file structure and code organization. Is it clean and well-structured?",
            "Examine the choice of technologies and frameworks. Are they appropriate for the problem?",
            "Look at the source code quality — naming, modularity, separation of concerns.",
            "Check for configuration files (package.json, requirements.txt, etc.) — are dependencies reasonable?",
            "Assess the commit history — does it show iterative development and meaningful progress?",
            "Rate the overall technical soundness on a scale of 1-5, where 1 is poor and 5 is excellent.",
        ],
    },
    {
        "dimension": "feature",
        "name": "Feature Alignment",
        "weight": 0.25,
        "criteria": (
            "Evaluate how well the project delivers on its stated goals. "
            "Compare the project description and pitch with what the code actually implements. "
            "Consider feature completeness, functionality depth, and whether the demo matches the promise."
        ),
        "evaluation_steps": [
            "Read the project description/pitch and identify the key features promised.",
            "Examine the codebase to verify which features are actually implemented.",
            "Assess the depth of each feature — is it a stub or a working implementation?",
            "Check if the README documents how to use the features.",
            "Consider whether the project scope is appropriate for a hackathon timeframe.",
            "Rate the feature alignment on a scale of 1-5, where 1 is mostly unimplemented and 5 is fully delivered.",
        ],
    },
    {
        "dimension": "uiux",
        "name": "UI/UX Innovation",
        "weight": 0.20,
        "criteria": (
            "Evaluate the user interface and user experience aspects of the project. "
            "Consider design quality, usability, accessibility, innovative interaction patterns, "
            "and overall polish of the frontend or user-facing components."
        ),
        "evaluation_steps": [
            "Look at frontend code (components, styles, layouts) for design quality.",
            "Assess the navigation flow and information architecture from the code structure.",
            "Check for responsive design, accessibility considerations, and error states.",
            "Evaluate any innovative or creative UI/UX patterns used.",
            "Consider the overall user experience implied by the code and README screenshots.",
            "Rate the UI/UX innovation on a scale of 1-5, where 1 is minimal/no UI and 5 is exceptional.",
        ],
    },
    {
        "dimension": "freshness",
        "name": "Code Freshness",
        "weight": 0.25,
        "criteria": (
            "Evaluate whether this project was genuinely built during the hackathon. "
            "Look for signs of fresh development vs. pre-existing code being repurposed. "
            "Consider commit patterns, code consistency, and whether the code appears to be "
            "written as a cohesive unit rather than assembled from disparate pre-built parts."
        ),
        "evaluation_steps": [
            "Analyze the commit history — are commits spread over the hackathon period?",
            "Check for initial scaffolding commits followed by feature development.",
            "Look for code style consistency — does it appear written by the same team?",
            "Check if the project uses standard templates/boilerplate (acceptable) vs. pre-built features (not acceptable).",
            "Assess whether the complexity matches what could reasonably be built in a hackathon.",
            "Rate the code freshness on a scale of 1-5, where 1 is clearly pre-existing and 5 is clearly fresh.",
        ],
    },
]
