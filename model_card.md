# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Name: AudioFinder 1.0
---

## 2. Intended Use  


- The recommender is designed to recommend 5 songs that a user will like and enjoy based on the genre, mood, energy, and tempo inputted by the user. It will predict songs close or related to the user's inputs. Thi system is meant for users trying to find new songs they want to listen to based on what they already listen to currently.

---

## 3. How the Model Works  


- The program works by first taking input the 4 features I chose, which are genre, mood, energy, and tempo. Each feature is worth a certain amount of points, and some features can be worth more than others, depending on what the user inputs. This model turns the user input into a score by comparing each song in the songs.csv file to the user input. With Genre and Mood, it checks if a song in the file matches the user input, then awards points based on the result. Then, with energy and tempo, those are calculated numerically. Both are calculated on a 0-1 scale, and then multiplied by the amount worth of each feature. Finally, all those points are added up, and the top 5 songs with the highest final scores are displayed as recommended. 

---

## 4. Data  
  

- There is a total of 15 songs in the catalog. Some genres that are represented are pop, lofi, rock, and intense. I added 5 songs so there could be a bigger range of songs to choose from, with more genres as well. The data set is still missing other genres and moods, which can help with the recommending and not overprioritizing of genres.

---

## 5. Strengths  


- User types for which the system gives reasonable results are users who prefer pop genre with a happy mood. The scoring correctly captures reasonable energy and tempo inputs, and have matched my intuition when inputting different user profiles. 
---

## 6. Limitations and Bias 

- One weakness that was discovered during the testing process is that since the change of doubling the energy, although it was much more accurate on the recommendations, it can hurt users with mixed taste. Users that have mutliple genre/moods with the same energy level can be recommended very specific songs mutliple times, instead of more of a range of songs. This can lead to repeated songs being recommended overall.

## 7. Evaluation  


- The way I checked whether the recommender behaved as expected was looking through the logic and math functionality when inputing user profiles. I double checked the math to ensure no logic errors and that the system properly displayed the correct information.


- Some user profiles I tested were:
1. Listeners who like upbeat songs
-  Pop,happy, high energy, and high tempo

2. - Listeners who prefer pop songs that are energetic but feel smoother
- Pop, chill, high energy, steady tempo


3. - Listeners who enjoy futuristic, experimental pop sounds
Hyperpop,euphoric, energy higher than average, and high tempo 

4. - Listeners who choose depend mostly on how fast or energetic a song is
Purely energy and tempo based (No genre or mood inserted)


5. - Listeners who mainly care about genre and mood
Purely Genre and Mood based (NO energy or tempo inserted)


---

## 8. Future Work  


- An additional feature I would add to improve the system is out of range tempo and energy. Inputting numbers like 0 in range and energy make it so there are logic errors in the process and output. Having set the actual range will help. 
- Also, adding much more songs to the songs.csv file will help much more in keeping all genres and moods fair to be chosen. 
---

## 9. Personal Reflection  
 

- I learned that recommender systems have 2 different ways of working, which is collaborative filtering and user-based filtering.
- Something interesting I discovered is how math and numeric calculations are used to best show the score and similarness of different songs.
- This changed the way I think about music recommendation apps by showing how there is much more math and logic to implement to have a fully functional system with no random recommendations and errors.
