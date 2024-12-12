# prompt_generator.py

class PromptManager:
    def __init__(self):
        self.system_prompts = {
            "analyze_image_risks": """

                You are an expert with doctoral-level knowledge in the field of “Industrial Safety” and “Risk Assessment” working for POSCO, a South Korean steel company. The image provided to you is a potential hazard (a situation where something dangerous is likely to happen) reported by a coworker who is working in a steel mill plant.
                **Task**: Analyze the provided image and generate a comprehensive safety risk analysis report based on the following criteria:
                **Requirements**:
                1. **Risk Elements Identification**: Identify all potential risk elements visible in the image. For example, "slippery surface," "worker operating at height," etc. Provide a detailed description for each.
                2. **Risk Level Assessment**: Assess how dangerous each risk element is by categorizing it with a numeric scale from A to E, where A indicates the most critical risk and E indicates a minimal risk. Provide a brief explanation for each classification:
                    - **A (Critical)**: A situation where an accident or injury is imminent and could occur immediately.
                    - **B (High)**: A situation where an accident or injury is likely to occur in the near future.
                    - **C (Medium)**: A situation where there is a 50% probability of an accident occurring.
                    - **D (Low)**: A situation where an accident is unlikely but still possible under rare circumstances.
                    - **E (Minimal)**: A situation with very low or negligible risk of accident or injury.
                3. **Risk Scenario Simulation**: For each identified risk, simulate a potential accident or incident scenario. Example: 'A worker might slip on the wet surface and sustain injuries.'
                4. **Mitigation Measures**: Propose specific safety measures or actions to address each identified risk. For example, "Slippery surface: Install anti-slip mats or place warning signs."
           
            """,
            "format_risk_as_json": """

                You are a highly skilled assistant specializing in converting plain-text risk analysis into a structured JSON format.
                Your task is to convert the provided risk analysis report into a structured JSON format, extracting the following information:
                - The identified risks and their severity.
                - Suggested mitigation measures for each risk.
                Ensure that the format adheres to the schema provided by the user in the input.
                Focus on accuracy, clarity, and adherence to the schema, and ignore irrelevant details.

            """,
            "retrieve_information": """

                You are an assistant skilled in summarizing structured risk analysis data. 
                Your task is to generate a concise summary based on a structured JSON array containing safety-related risks, risk levels, simulation scenarios, and associated keywords for each risk. 
                The summary should include the following elements:
                1. **Index and Risk Level** 
                2. **Detailed Risk Information** - including risk type, simulation scenario, and **key improvements** 
                3. **Keywords related to the risk** 
                4. **Responsible manager** identified in the provided documents 
                5. **Document Information** - such as document title and summary
                The entire response must be written in Korean.

            """
        }

        self.user_prompts = {
            "analyze_image_risks": """

                ## Instruction
                You are a PhD-level expert in the field of “industrial safety” and “risk assessment” working for POSCO, a South Korean steel company. The image provided to you is a potential hazard (a situation where something dangerous is likely to happen) reported by a coworker who works in a steel mill plant.
                Your task is to:
                1. Analyze the image and identify **major potential safety hazards**.
                2. For each hazard:
                - Identify the hazard.
                - Assess the risk level using a scale from A to E (where A is the highest risk and E is the lowest).
                    - **A (Critical)**: A situation where an accident or injury is imminent and could occur immediately.
                    - **B (High)**: A situation where an accident or injury is likely to occur in the near future.
                    - **C (Medium)**: A situation where there is a 50% probability of an accident occurring.
                    - **D (Low)**: A situation where an accident is unlikely but still possible under rare circumstances.
                    - **E (Minimal)**: A situation with very low or negligible risk of accident or injury.
                - Simulate potential accident scenarios related to the hazard.
                - Suggest actionable recommendations for improving safety related to that hazard.
                3. Write all of your analysis **in Korean**.

                ### Example Output Structure:
                ```
                ### 위험성 분석 레포트
                1. **위험 요소**
                - 위험 요소: [위험 요소에 대한 설명]

                2. **위험 수준 평가** (위험 수준 알파벳이 A에 가까워질수록 위험도가 높음)
                - 위험 요소명 : [위험 수준 (A/B/C/D/E)] - [평가 이유]

                3. **위험 상황 시뮬레이션**
                - 위험 요소명 : [발생 가능한 사고나 상황에 대한 시뮬레이션을 가능한 상세하게 설명하세요.]

                4. **조치 방법**
                - 위험 요소명: [제안된 조치 방법에 대해서 가능한 상세하게 설명하세요.]

                5. **기타 정보**
                - 유저 코멘트: [유저가 올린 코멘트]
                - 유저 위치: [유저가 올린 위치]

                ```

                ## Input:
                The image is provided as a Base64-encoded string.  
                Please analyze this image, **considering both the user's comment and location information**, and provide your response strictly in Korean using the above-specified Markdown format.  
   
            """,
            "format_risk_as_json": """
               
                ## Instruction 
                The following task involves organizing information into a **structured JSON format** based on the provided schema. Each entry in the array should include the following fields and adhere to these guidelines:
                - `index`: An integer that serves as a unique identifier for each entry.
                - `riskLevel`: A string indicating the severity of the identified risk. Choose one of the following predefined levels: A to E (where A represents the highes risk and E represents the lowest risk).
                - `content`: A nested object containing detailed information about the identified risk and its management. It should include:
                    - `potentialRisk`: A string representing the type of potential risk. Choose one of the following predefined categories:
                    [`가스중독 및 질식`, `감전`, `교통`, `기타`, `낙하 및 비래`, `무리한동작`, `베임`, `붕괴 및 도괴`, `업무상질병`, `유해물접촉`, `이상온도접촉`, `전도`, `찔림`, `추락`, `충돌 및 격돌`, `파열`, `폭발`, `협착`, `화재`]
                    - `mitigationPlan`: A string providing a proposed plan to mitigate or address the identified risk.
                    - `simulation`: A string detailing the simulation performed to evaluate or address the risk. Include the method used, conditions simulated, expected outcomes, and any relevant observations.
                    - `keywords`: An array of exactly three strings, extracted from the content, that represent key terms for search and indexing purposes. These should include significant terms such as the potential risk, key elements of the mitigation plan, and notable points from the simulation.

                ### Key Usage:
                1. **Risk Level Field**:
                - **Description**: Assign a risk assessment level between A (highest risk) and E (lowest risk) and  based on the severity of the identified risk. The risk level should be determined by evaluating the potential impact and probability of the risk event.
                - **Action**: Provide a numeric value (A to E) representing the risk severity. Ensure that the risk level accurately reflects the overall danger of the situation.
                2. **Content Field**:
                - **Potential Risk**:
                    - **Description**: Identify the type of risk from the predefined categories (e.g., '가스중독 및 질식', '감전', '교통', etc.). This should be chosen based on the nature of the risk described.
                    - **Action**: Select one of the predefined categories that best represents the identified risk.
                - **Mitigation Plan**:
                    - **Description**: Provide a safety improvement recommendation or action plan to mitigate the identified risk. The plan should be actionable, clear, and contextually relevant to the risk type.
                    - **Action**: Write a concise, specific plan that can help reduce or eliminate the risk. Ensure that the recommendation directly addresses the risk in a practical manner.
                - **Simulation**:
                    - **Description**: Document the details of any simulations performed to assess the risk. This should include the method used, conditions simulated, expected outcomes, and relevant observations that help in understanding how the risk behaves under certain conditions.
                    - **Action**: Provide detailed information about the simulation, including the purpose, methodology, and key results or insights that help inform risk management decisions.
                3. **Keywords Field**:
                - **Description**: Extract 3 significant keywords from the content to facilitate search and indexing. These should capture the most important aspects of the risk evaluation, such as the type of potential risk, key aspects of the mitigation plan, or notable findings from the simulation.
                - **Action**: Choose exactly 3 keywords that best represent the risk evaluation entry. These should be relevant, distinct, and help in quick identification or retrieval of similar records in a system.

                ### Output Schema:
                {{
                    "type": "object",
                    "properties": {{
                        "index": {{
                            "type": "integer",
                            "description": "The unique identifier for the risk assessment entry."
                        }},
                        "riskLevel": {{
                            "type": "string",
                            "enum": ["A", "B", "C", "D", "E"],
                            "description": "The risk assessment level, where A represents the highest risk and E represents the lowest risk."
                        }},
                        "content": {{
                            "type": "object",
                            "properties": {{
                                "potentialRisk": {{
                                    "type": "string",
                                    "enum": ["가스중독 및 질식", "감전", "교통", "기타", "낙하 및 비래", "무리한동작",
                                            "베임", "붕괴 및 도괴", "업무상질병", "유해물접촉", "이상온도접촉", "전도",
                                            "찔림", "추락", "충돌 및 격돌", "파열", "폭발", "협착", "화재"],
                                    "description": "The type of potential risk. Choose one of the predefined categories."
                                }},
                                "mitigationPlan": {{
                                    "type": "string",
                                    "description": "The plan to mitigate the risk. Express in three steps what you need to do to ensure safety. The steps should end with a Korean noun or a Korean command ending. Break the line at the end of each step."
                                }},
                                "simulation": {{
                                    "type": "string",
                                    "description": "Simulation scenario of the risk occurrence. Write a detailed description of the hazardous situation that could occur if safety measures are not taken."
                                }}
                            }},
                            "required": ["potentialRisk", "simulation"],
                            "description": "A nested object containing detailed information about risks and their management."
                        }},
                        "keywords": {{
                            "type": "array",
                            "items": {{
                                "type": "string"
                            }},
                            "description": "A list of keywords extracted from the content for search and indexing purposes. Keywords should include significant terms such as the potential risk, key elements of the mitigation plan, and notable points from the simulation. Write exactly 3 keywords."
                        }},
                        "comment": {{
                            "type": "string",
                            "description": "User's comment while reporting the risk."
                        }},
                        "location": {{
                            "type": "string",
                            "description": "User's location information."
                        }}
                    }},
                    "required": ["index", "riskLevel", "content", "keywords", "comment", "location"],
                    "description": "An object representing a single risk evaluation entry, including user comments and location."
                }}


            """,
            "retrieve_information": """

                ## Instruction
                The following is a **Risks JSON** containing analyzed risks and recommendations. Summarize this information using the specified format.

                ## Document Information 
                The following is the content of the document. 
                The document contains details about the managers responsible for potential risks and past risk cases. 
                This document is a casebook from POSCO, a leading steel company in South Korea, outlining actions taken regarding specific `potentialRisk` scenarios.

                ### Output Schema:
                {{
                    "type": "object",
                    "properties": {{
                        "index": {{
                            "type": "integer",
                            "description": "Unique identifier for the risk."
                        }},
                        "riskLevel": {{
                            "type": "string",
                            "enum": ["A", "B", "C", "D", "E"],
                            "description": "The risk assessment level, where A represents the highest risk and E represents the lowest risk."
                        }},
                        "content": {{
                            "type": "object",
                            "description": "Detailed content about the risk.",
                            "properties": {{
                                "potentialRisk": {{
                                    "type": "string",
                                    "description": "The identified potential risk.",
                                    "enum": ["가스중독 및 질식", "감전", "교통", "기타", "낙하 및 비래", "무리한동작",
                                            "베임", "붕괴 및 도괴", "업무상질병", "유해물접촉", "이상온도접촉", "전도",
                                            "찔림", "추락", "충돌 및 격돌", "파열", "폭발", "협착", "화재"]
                                }},
                                "mitigationPlan": {{
                                    "type": "string",
                                    "description": "The plan to mitigate the risk. Express in three steps what you need to do to ensure safety. The steps should end with a Korean noun or a Korean command ending. Break the line at the end of each step."
                                }},
                                "simulation": {{
                                    "type": "string",
                                    "description": "Simulation scenario of the risk occurrence. Write a detailed description of the hazardous situation that could occur if safety measures are not taken."
                                }}
                            }},
                            "required": ["potentialRisk", "mitigationPlan", "simulation"]
                        }},
                        "comment": {{
                            "type": "string",
                            "description": "User's comment while reporting the risk."
                        }},
                        "location": {{
                            "type": "string",
                            "description": "User's location information."
                        }},
                        "keywords": {{
                            "type": "array",
                            "description": "List of keywords related to the risk.",
                            "items": {{
                                "type": "string"
                            }}
                        }},
                        "manager": {{
                            "type": "object",
                            "description": "Details of the manager associated with the risk.",
                            "properties": {{
                                "name": {{
                                    "type": "string",
                                    "description": "Name of the manager."
                                }},
                                "department": {{
                                    "type": "string",
                                    "description": "Department of the manager."
                                }},
                                "phonenumber": {{
                                    "type": "string",
                                    "description": "Contact phone number of the manager."
                                }},
                                "email": {{
                                    "type": "string",
                                    "description": "Contact email of the manager."
                                }}
                            }},
                            "required": ["name", "department", "phonenumber", "email"]
                        }},
                        "documents": {{
                            "type": "object",
                            "description": "Details of a single document related to the risk.",
                            "properties": {{
                                "title": {{
                                    "type": "string",
                                    "description": "Title of the document."
                                }},
                                "document_summary": {{
                                    "type": "string",
                                    "description": "Summary of the document."
                                }}
                            }},
                            "required": ["title", "document_summary"]
                        }}
                    }},
                    "required": ["index", "riskLevel", "content", "comment", "location", "keywords", "manager", "documents"]
                }}

            """
        }

        self.tools = {
            "format_risk_as_json": {
                "type": "function",
                "function": {
                    "name": "output_risks_json",
                    "description": "Converts analyzed risks into a structured JSON format based on the specified schema, including index, riskLevel, content, and keywords.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "object",
                                "properties": {
                                    "index": {
                                        "type": "integer",
                                        "description": "The unique identifier for the risk assessment entry."
                                    },
                                    "riskLevel": {
                                        "type": "string",
                                        "enum": ["A", "B", "C", "D", "E"],
                                        "description": "The risk assessment level, where A represents the highest risk and E represents the lowest risk."
                                    },
                                    "content": {
                                        "type": "object",
                                        "properties": {
                                            "potentialRisk": {
                                                "type": "string",
                                                "enum": ["가스중독 및 질식", "감전", "교통", "기타", "낙하 및 비래", "무리한동작",
                                                        "베임", "붕괴 및 도괴", "업무상질병", "유해물접촉", "이상온도접촉", "전도",
                                                        "찔림", "추락", "충돌 및 격돌", "파열", "폭발", "협착", "화재"],
                                                "description": "The type of potential risk. Choose one of the predefined categories."
                                            },
                                            "mitigationPlan": {
                                                "type": "string",
                                                "description": "The plan to mitigate the risk. Express in three steps what you need to do to ensure safety. The steps should end with a Korean noun or a Korean command ending. Break the line at the end of each step."
                                            },
                                            "simulation": {
                                                "type": "string",
                                                "description": "Simulation scenario of the risk occurrence. Write a detailed description of the hazardous situation that could occur if safety measures are not taken."
                                            }
                                        },
                                        "required": ["potentialRisk", "simulation"],
                                        "description": "A nested object containing detailed information about risks and their management."
                                    },
                                    "keywords": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        },
                                        "description": "A list of keywords extracted from the content for search and indexing purposes. Keywords should include significant terms such as the potential risk, key elements of the mitigation plan, and notable points from the simulation. Write exactly 3 keywords."
                                    },
                                    "comment": {
                                        "type": "string",
                                        "description": "User's comment while reporting the risk."
                                    },
                                    "location": {
                                        "type": "string",
                                        "description": "User's location information."
                                    }
                                },
                                "required": ["index", "riskLevel", "content", "keywords", "comment", "location"],
                                "description": "An object representing a single risk evaluation entry, including user comments and location."
                            }
                        },
                        "required": ["data"]
                    }
                }
            },
            "retrieve_information": {
                "type": "function",
                "function": {
                    "name": "nearmiss_details",
                    "description": "Provides detailed information about identified risks, their mitigation plans, related personnel, and associated documents.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "risks": {
                                "type": "object",
                                "properties": {
                                    "index": {
                                        "type": "integer",
                                        "description": "Unique identifier for the risk."
                                    },
                                    "riskLevel": {
                                        "type": "string",
                                        "enum": ["A", "B", "C", "D", "E"],
                                        "description": "The risk assessment level, where A represents the highest risk and E represents the lowest risk."
                                    },
                                    "content": {
                                        "type": "object",
                                        "description": "Detailed content about the risk.",
                                        "properties": {
                                            "potentialRisk": {
                                                "type": "string",
                                                "description": "The identified potential risk.",
                                                "enum": ["가스중독 및 질식", "감전", "교통", "기타", "낙하 및 비래", "무리한동작",
                                                        "베임", "붕괴 및 도괴", "업무상질병", "유해물접촉", "이상온도접촉", "전도",
                                                        "찔림", "추락", "충돌 및 격돌", "파열", "폭발", "협착", "화재"]
                                            },
                                            "mitigationPlan": {
                                                "type": "string",
                                                "description": "The plan to mitigate the risk. Express in three steps what you need to do to ensure safety. The steps should end with a Korean noun or a Korean command ending. Break the line at the end of each step."
                                            },
                                            "simulation": {
                                                "type": "string",
                                                "description": "Simulation scenario of the risk occurrence. Write a detailed description of the hazardous situation that could occur if safety measures are not taken."
                                            }
                                        },
                                        "required": ["potentialRisk", "mitigationPlan", "simulation"]
                                    },
                                    "comment": {
                                        "type": "string",
                                        "description": "User's comment while reporting the risk."
                                    },
                                    "location": {
                                        "type": "string",
                                        "description": "User's location information."
                                    },
                                    "keywords": {
                                        "type": "array",
                                        "description": "List of keywords related to the risk.",
                                        "items": {
                                            "type": "string"
                                        }
                                    },
                                    "manager": {
                                        "type": "object",
                                        "description": "Details of the manager associated with the risk.",
                                        "properties": {
                                            "name": {
                                                "type": "string",
                                                "description": "Name of the manager."
                                            },
                                            "department": {
                                                "type": "string",
                                                "description": "Department of the manager."
                                            },
                                            "phonenumber": {
                                                "type": "string",
                                                "description": "Contact phone number of the manager."
                                            },
                                            "email": {
                                                "type": "string",
                                                "description": "Contact email of the manager."
                                            }
                                        },
                                        "required": ["name", "department", "phonenumber", "email"]
                                    },
                                    "documents": {
                                        "type": "object",
                                        "description": "Details of a single document related to the risk.",
                                        "properties": {
                                            "title": {
                                                "type": "string",
                                                "description": "Title of the document."
                                            },
                                            "document_summary": {
                                                "type": "string",
                                                "description": "Summary of the document."
                                            }
                                        },
                                        "required": ["title", "document_summary"]
                                    }
                                },
                                "required": ["index", "riskLevel", "content", "comment", "location", "keywords", "manager", "documents"]
                            }
                        },
                        "required": ["risks"]
                    }
                }
            }
        }


    def get_system_prompt(self, task_name):
        return self.system_prompts.get(task_name, "Task not found.")

    def get_user_prompt(self, task_name):
        return self.user_prompts.get(task_name, "Task not found.")

    def get_tool(self, task_name):
        return self.tools.get(task_name, "Tool not found.")


class AnalyzeImageRisks(PromptManager):
    def get_system_prompt(self):
        return super().get_system_prompt("analyze_image_risks")

    def get_user_prompt(self, comment, location):
        user_prompt = super().get_user_prompt("analyze_image_risks")
        user_prompt += "\n"
        user_prompt += f"### User Comment :\n{comment}\n\n"
        user_prompt += f"### User Location :\n{location}\n"
        return user_prompt


class FormatRiskAsJson(PromptManager):
    def get_system_prompt(self):
        return super().get_system_prompt("format_risk_as_json")

    def get_user_prompt(self, analyzed_image_risks):
        return super().get_user_prompt("format_risk_as_json") + f"### Input Text :\n{analyzed_image_risks}\n"

    def get_tool(self):
        return super().get_tool("format_risk_as_json")


class RetrieveInformation(PromptManager):
    def get_system_prompt(self):
        return super().get_system_prompt("retrieve_information")

    def get_user_prompt(self, doc_search_keyword, document_text, formatted_risks_json):
        user_prompt = super().get_user_prompt('retrieve_information')
        user_prompt += f"### **Risks JSON**:\n{formatted_risks_json}\n"
        user_prompt += f"\n### Related Documents\n-Find the **mitigationPlan**, **manager**, and **documents** in the below document, and respond in the above specified schema format:\n"
        user_prompt += f"\n#### Document Title: 잠재위험 사례집 _ {doc_search_keyword}.docx"
        user_prompt += f"\n#### Document Contents:\n{document_text}\n"
        return user_prompt

    def get_tool(self):
        return super().get_tool("retrieve_information")

