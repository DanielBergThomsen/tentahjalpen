### Current issues and essential features

Make backend send email when receiving exam suggestion 
- Give option to grant or deny directly in email
- Email contains pdf and details
- Allow safe interaction with API by providing temporary URL to grant/deny

Slider for only displaying a certain amount of exams: 
https://github.com/jerairrest/react-chartjs-2/issues/246
https://github.com/chartjs/chartjs-plugin-zoom - this or vizwit??

Current logic between ExamAnalytics and ExamPanel is convoluted to say the least:
-Don't use component function to change the displayed data, pass as prop.
-Add tests for the ExamPanel

Add course link in comparison table entries

Add search bar navigation using arrow keys

Draw suggestion into own subcomponent to avoid onClick function creation for every instance

Expand GA functionality by following user interactions

Add modal for when uploading a file fails

Prompt user only to upload a pdf when choosing files from computer

Use Redis instead of saving file locally so that multiple workers do not attempt to
update different files

Find a prettier way of dealing with JSONifying errors

Make use of blueprints instead of inserting every function in the app factory

Can't run scrape more than once per session - low priority

Add snapshot testing

### Ideas

Support for Anki decks

Try exam difficulty prediction

Add feature to compare overall difficulty with (all during that year?) other courses

Exam uploading instantly somehow
