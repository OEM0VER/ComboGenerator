# ComboGenerator
The application is designed to efficiently handle the generation of the maximum amount of possible combinations of files in a single folder, providing users with a flexible and user-friendly interface for ease of use.

# Details
The provided Python script is an application named "Combination Generator" created using the Tkinter library for the graphical user interface (GUI). Here's a brief description of what the app does:

Combination Generator by M0VER
This application allows users to generate combinations of files from a specified input folder and save them to an output folder. The key features and components of the app are as follows:

Input and Output Folders:

Users can choose the input and output folders through the GUI. The input folder should contain files that the user wants to combine in different permutations.
Files per Combination:

The user can specify the number of files to be combined in each permutation through the "Files per Combination" entry.
Combination Calculator:

The app includes a feature to calculate the number of combinations (C(n, r)), where "n" is the total number of files in the input folder, and "r" is the user-specified number of files per combination.
Generate Combinations Button:

Clicking the "Generate Combinations" button initiates the process of creating combinations based on user input. The app displays the progress and estimates the output size.
Stop Process Button:

Users can stop the combination generation process at any time by clicking the "Stop Process" button.
Status Updates:

The app provides status updates on the progress of the combination generation process.
User Interface:

The GUI features tooltips for various elements, a clickable image with a URL link, and a signature indicating the creator (M0VER).
Configuration File:

The app uses a configuration file (config.ini) to store and load user preferences, such as input/output folder paths and the number of files per combination.
Threaded Execution:

The combination generation process runs in a separate thread to avoid freezing the GUI during the operation.
Exit Handling:

The app saves user preferences when the user closes the application.
Icon and Image:

The app sets an icon and includes a round image with a link to the creator's profile.
Designed by M0VER:

The app includes a signature indicating that it was designed and created by M0VER.
The application is designed to efficiently handle the generation of combinations, providing users with a flexible and user-friendly interface for file manipulation.
