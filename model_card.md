# 🎧 Model Card: AMPED, The AI DJ

## 1. Model Name  

AMPED
---

## 2. Intended Use  

- The recommender is designed to  recommend top songs based on what the user looks is looking for. The user has two modes to choose from, describe mode: The user described what they want(Ex: "Something chill for studying"), and artist mode, the user enters an artist they want music recommendations from.

---

## 3. How the Model Works  

- The model works by implementing RAG. When the user enters input, the system uses a rule-based retrieval approach to find similarities to the query the user has entered. Songs are searched for and retrieved in a music file that has many songs, each with more information and features describing them. After retrieval, the system has guardrails in place to ensure that the songs retrieved fit the description of what the user is looking for. Since songs are scored to determine what the top songs are, there are quality gates, that ensure that the songs must be above a certain point threshold to be considered a "strong" suggestion. Once the retrieved song are passed, they are sent to the Gemini model. The Gemini model helps in displaying the results clearly with an explanation on why those were suggested for the user. 
---

## 4. Data  
  
- There is a total of 1,685 songs in the catalog. There is are many different kinds of artists, as well as different genres of music, so the user won't have to limit their searches. The file was obtained by the Kaggle Wesbite. 

---

## 5. Strengths  

- The system overall performs well when in proper use. The system correctly formats and uses Gemini to help display and give the user proper recommendations, as well as explanations to why those are songs best fit for their search. Also, the UI is very straightforward, and the user should not have a hard time understanding what the point of the program is.

---

## 6. Limitations and Bias 

- A limitation towards the system is that the program may have a harder time dealing with un-common descriptions of what the user may want. Since the system uses more of a rule-based approach, it can sometimes skip over more complex descriptions. The system could be better improved to handle those kinds of inputs better. Another limitation towards the system is that it will have a harder time dealing with inputs that can be misspelled, like in the artist mode. If a user mispells an artist's name, the system might skip over songs that belong to what the user means.

---

## 7. Evaluation  

- To ensure the proper functionality of the RAG system, there are pytests in place for things like:

- Retrieval: to ensure what is retrieved is a strong suggestion

- Ensuring enough songs are retrieved: if not enough songs are retrived the system will not display recommendations

- Ensuring Gemini to clearly display context sent, and to not hallucinate any answers.

---

## 8. Future Work  


- Something I would definitely look into is more towards implementing vector embedding, the process of turning text into numbers, so meanings can be compared mathematically. This will improve the overall comparison project, and will help eliminate the limits to un-common phrases that a user inputs. To add this to the system there will have to be an embedding model added, and this will help with the ranking process. 
---

## 9. Personal Reflection  
 
- Extending this project onto a RAG based project helped me understand how a RAG system really works. It helped me learn that the way a system retrieves information needed is crucial, and should be very well implemented to have a functional working RAG program. Copilot helped in clearning any confusion I had while developing the project, and since I know more about how these types of systems work, I am excited to develop more types of projects with them.
