# Greetings
This is a general personal setup I am currently Using. You can probably see below - 
![What will it look like in Tmux](Screenshots/Screenshot.png)
With all intents and purposes consider this a Working prototype. Most of it is AI Generated and personally All code written by AI should be treated as Prototype only.


## Genral Folder Structure is something like
```
.personal_bash_config
Tasks/
│
├── updater.py
├── daily_logger.exe -> Compile this file using -lncurses -lpaner and give a name and include the exe file
├── Timeline-Tasks.csv
├── gui.py
├── logo.txt
```


Even after this, this whole setup might not work. At this current stage this is not reporducible

## Current Problems 
1) A lot of this is Gen-AI written code. This needs to be re-factored some day
2) Proper False case scenario at each stage
3) Proper GUI.py code structure - with seperate files denoting what stage
4) Refactoring of Graphs and solving their issues 
5) Better GUI main tab and TAsk addition Tab
6) Proper Diagrams and Documentation of some kind of what to expect and how to react
7) Some animations in Ncurses would be nice
8) Proper Updater file
9) Probably adding lua files for nvim in the future
10) Implementation of Post Completion "Section"
11) Better handling of Subtask info
12) Removal of reduntant datum like PredictionAccuracy in Time_Taken_Until column
13) Better implementation and usage of Progress Till (Basically from say 15% to something like 10_2_3 so as to better co-ordinate with What session how much progress was made)
14) Currently only one HAlt is allowed which is limiting hence - Allowing of multiple Halts 



## General Overview of Logger
This project's main objective was to have easily configurable and easily sharable Logger List along with Complex Dashboards. This potentially meant that Logger List needed to be a common file format like csv and the 
Logger file would be configurable by some scripts and programs which help in acting as Abstractations. Particularly this project in essence is not NOVELTY or industry-breaking, Armageddon reckoning concept
but rather a personal hobby project. I wanted something that I made myself(This is eventually broken with the use of GenAI Code, I am working on it to remove that) without external downloads or libraries or something.
Essentially the Motivation of this project was to have 
> "Authentic existence demands a private liturgy of organization. When the 'Other' imposes its structures, it brings the entropy of the alien.
> Only the internal mechanism—forged in the heat of self-awareness—operates with the silence of true independence"
This does not means we should re-invent the wheel for the sake of Flying across oceans. But we should have control and knowledge over the object that decides our daily personal life. 
As a demonstrative example Here are some screenshots of what This would probably look like -









Here is the Desctiption of Logger. Same content is there in the ![Txt FIle](Timneline-Tasks-Desc.txt)
1) Tasks
2) Description
3) Prediction Time - How much time do you think This will take to complete? (Default - 36 Hours)
4) Priority - Range value from 1 to 10
5) Tags
6) Status - One of 6 states a Task can be in "Uninitiated,Ongoing,Halted,Dropped,Completed,Post Completion"
7) Substasks
8) Time Taken Until - A little combination of four different datam -
        PreInitiationPeriod -> Time period of Task under which it is in Uninitiation
        Labor - Time Spent per task
        PredictionAccuracy - % between Labor and Prediction Time, Can be more then 100%
        Halting Time - How much time is the task inside Halted Stage
9) Progress Till - Self report value of how much work has been completed (Generally asked as % and can go over 100)
10) Project Folder Location
11) Estimated Effort Points - Combination of EF values asked at three different occasions in a Task Lifecycle 1)At Declaration 2) At Halting 3) At completion
12) Dates - Important dates, acting as timestamp

I shall explain where what I am dealing as a Lifecycle of Tasks here - It goes something like


```
/====================================================================\
|  TASK: %Task_Name%                                    PRIORITY: [8] |
|--------------------------------------------------------------------|
|  DESC: %Description%                                               |
|  LOC : ~/dev/projects/void_engine/                                 |
|--------------------------------------------------------------------|
|  PREDICTION: 36.00 hrs             ACCURACY: [ %%%.%% ]            |
|  EFFORT PTS: [ iii _ iii _ iii ]   PROGRESS: [ ###/100 ]           |
|--------------------------------------------------------------------|
|  TIMELINE:                                                         |
|  Decl. -> Init. -> Ongo. -> Halt. -> Comp.                         |
|  11/02 _ 12/02 _ 15/02 _  --   _  --                               |
\====================================================================/
```


```
[ 01: DECLARATION ]  <-- The Word is Spoken (Date_of_Decl)
               |
               v
      [ 02: UNINITIATED ]  ---( Pre-Initiation Period )---
               |                                         |
      { EF: iii _ _ }                                    |
               |                                         |
               v                                         v
      [ 03:  ONGOING    ] <-------------------------[ 04: HALTED     ]|
      |                 |       (Empty Labor)       |                 |
      |   "THE LABOR"   | ------ [ 21 Days ] ------>| { EF: _ iii _ } |
      | (HHH.MM / %%%)  |                           |                 |
      |                 | <----- [ NEW LABOR ] -----|                 |
      +-----------------+                           +-----------------+
               |                                         |
               |                                   (Empty Labor)
               v                                   [ 90 Days ]
      [ 05: COMPLETED   ]                                |
      |                 |                                v
      | { EF: _ _ iii } |                        [ 06:  DROPPED  ]
      +-----------------+                        ( The Data Death )
               |
               v
      [ 07: POST-COMPLETION ]
      ( The Teleological Echo )
```

I am showcasing 16 proably different visuals along 4 tabs in the GUI. A peak into that is something like - 
Here is the description of Visuals that in the Gui

Tab I - "Work Effort Progress and other Abstractions"
1) Pie chart of Uninitiated,Ongoing,Halted,Dropped,Completed,Post Completion - "Historics record of how much have I conquered"
2) 
3) Progress vs Labor Time Series  for Last 7 active(recently activity of any kind which goes back full dates) task (Task name as color separation, - vs Dates of Ongoing vs Labor 
X - Axis - Date
Y - Axis  - Labor Hours 
Progress Till - Size of Scatter
Color - Task 
(How do we define last 7? - Those task which have recent activity of any kind) -  "Shows me how I am working on recent tasks"
4) Effort Points vs Priority graph - This would give a single matrix containing "Efforts vs Priority Graph and COlor them, Around the graph would be somewhere small list of 2 -3 tasks in each column - "Shows me what should be next task"


Tab II Name - "understanding Tags" (Options - Individual vs Grouped) 
1) Tags wise Priority - Bar Graph
2) Tags Wise average Prediction Time - Scatter plot with Task as Color
3) Tags wise Labor  and Effort Points - Scatter plot with Task as Color
4) Tags vs average session Progress


Tab III - "Hall of Halts and Dropped"
1) Estimated Effort Points Prediction Time   Labor Time and  number days of Halt- Average / Mean
2) Dropped vs Halt(Color distinction) Labour Time vs Dates
3) Common Tags for Halted and Common Tags for Dropping (Grouped for Task)
4) Dropped vs Halt(Color distinction) Progress Time vs Dates


Tab IV - "Is this end or Should we Transcend?"
1)  Lifecycle Time Breakdown - Show Graphs in four phases - Unintiated ,Halted, Completed Of Last 4 completed tasks. - Give Effort Points and prediction and overimpose labor and progress till  ????(I have no Idea How to be honest)
2) Estimated Effort Points Prediction Time   Labor Time and  number days of Completion - Average/Mean
3) Priority vs Completion Time vs Effort Values - Scatter Plot
4) Tags vs Completion (Individual vs Group)








     
