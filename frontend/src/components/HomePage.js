import React, { Component} from "react";

import
{
	Row,
	Col,
} from "react-bootstrap";


class HomePage extends Component
{
	render()
	{
		return(
			<Row className="mx-auto">
				<Col xs={12} md={10} lg={6} className="mx-auto">
					<h1 className="text-center">Hey there!</h1>
					<p>
							Welcome to Tentahjälpen!
							My ambition
							with this application is for it to aid you in your journey
							to become an engineer here at Chalmers University of Technology.
							You may already be familiar with a similar application written
							by <a href="http://tenta.bowald.se">another alumni.</a> That
								application has helped me, as well as many others, immensely.
								But it has its shortcomings. It is my ambition to fix these issues
								that I had with it, and then to provide a set of related features
								that might aid you, whether that be in helping you prepare for
								an upcoming exam, or help you choose between courses.
						</p>
						<h1 className="text-center">Why should I use this instead?</h1>
						<p>
								While there are several tiny improvements over Bowald's application
								in terms of the user interface, I will focus on actual metrics and features that
								I have added.
						</p>
						<p>
							<strong>Fail rate:</strong> While that has been somewhat remedied in a recent
								change to the application, my criticism still stands. Courses change
								over the years. The people who create the exams find better ways to
								test knowledge, lecturers hone their skill, and the people involved
								with the administration of the course also change. With this in mind,
								one might think that the perceived 'difficulty' of a course is impacted.
								And in a vast amount of cases, this is true. Therefore I consider it to
								be somewhat misleading to take exams statistics as far as 8 years ago
								into account when calculating such a metric. Here at Tentahjälpen, we
								only go back as far as three years when calculating our metric. Furthermore,
								while not as significant, there is also an inherent bias in the sampled
								data when looking at re-exams as opposed to the ordinary exams. Therefore,
								Tentahjälpen only looks at the non-re-exams.
						</p>
						<p>
							<strong>Mobile-friendly interface:</strong> Whether you're in class talking
								about some random course and trying to relate it to something you've experienced, or
								at home strategizing you education: you can count on Tentahjälpen to be at your
								side. No matter the size of the device you're using.
						</p>
						<p>
							<strong>Course comparison:</strong> Sometimes in life you don't need the added
								work load of taking the hardcore courses available to you. You might also
								have more than a few different courses that you are interested in. Sometimes,
								the amount of courses you can choose from might feel crippling to you. Luckily
								Tentahjälpen can help you get a bit of an overview of the various metrics associated
								with the exams for these courses. All you have to do is find the course codes for the
								courses you're interested in, and type them into Tentahjälpen's search bar. Tentahjälpen
								will give you a table of various metrics you can look at, and will also link you to a more
								detailed breakdown for each course as well.
						</p>
						<p>
							<strong>Looking at the actual exam:</strong> This was the feature that sparked the idea
								to begin with. You might be familiar with another <a href="https://chalmerstenta.se">website </a>
									that helps you with this. The thing is, it's sort of annoying jumping back and forth
									between the two websites when looking at old exams for a course you're taking. I thought
									to myself: "It would be way easier if I could just look at the exam I'm seeing the statistics
									for." And this is what I have done. A lot of the exams from chalmerstenta.se are available on
									the website, and you also have the ability to submit your own exams. In order to avoid the chaos
									associated with allowing the young Chalmerist to post whatever they want online, they are sent as
									'suggestions' to my database where I can then analyze the suggestion. If it's not trash, I will approve
									it and it will be available on the website.
							</p>
							<p>
								<strong>Fail rates over time:</strong> Want to know if a course is getting easier? With the 'rates' switch
									you can! Just head on over to your favorite course and press the slider. Now you will see a line chart
									with the various grade rates over time.
							</p>
							<p>
								<strong>Fancy bar chart:</strong> Want better intuition of the distribution of grades for any given exam?
									Just click the set of bars you want to examine and a pie chart will show up showing the percentages
									associated with the grades given in the exam. Below it you will find additional information given in
									text form, as well as either the ability to look at the exam or submit the pdf associated with it.
							</p>
						</Col>
					</Row>
		);
	}
}

export default HomePage;
