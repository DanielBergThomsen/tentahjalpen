import React, {Component} from "react";
import
{
	Bar,
	Line,
} from "react-chartjs-2";

import
{
	Row,
	Col,
	Table,
} from "react-bootstrap";

import ExamPanel from "./ExamPanel"

import colors from "../styles/colors.json";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import "../styles/exam_analytics.css";

class ExamAnalytics extends Component
{
	constructor(props)
	{
		super(props);
		this.state =
			{
				adjustedFailure: null,
				loaded:        false,
				failedLoading: false,
				showFailRate:  false,
				panelData:
				{
					taken:        null,
					examLink:     null,
					solutionLink: null,
					labels:       [],
					datasets:     [],
				},
				selectedData:
				{
					taken:        null,
					examLink:     null,
					solutionLink: null,
					labels:       [],
					datasets:     [],
				},
				courses:        [],
				rates:          [],
				averageData:    [],
			};

		this.examPanelElement = React.createRef();
		this.renderCourseFromList = this.renderCourseFromList.bind(this);
		this.toggleFailRate = this.toggleFailRate.bind(this);
		this.fetchCourse = this.fetchCourse.bind(this);
		this.coursesCallback = this.coursesCallback.bind(this);
		this.updateExamPanel = this.updateExamPanel.bind(this);
		this.resetExamPanel = this.resetExamPanel.bind(this);
		this.selectData = this.selectData.bind(this);
		this.prepareAvgData = this.prepareAvgData.bind(this);
		this.computeAdjustedFailure = this.computeAdjustedFailure.bind(this);
	}

	componentDidMount()
	{
		// codes should be unique as user is redirected on duplicates
		this.fetchCourses(this.props.codes);
	}

	componentDidUpdate()
	{
		window.scrollTo(
			{
				top: document.body.scrollHeight,
				left: 0,
				behavior: "smooth",
			});

		if(this.state.length === 0)
			this.resetExamPanel();
	}

	shouldComponentUpdate(nextProps, nextState)
	{

		// dumb hack to avoid weird internal issues with rendering in grouped bar chart
		if(this.state.showFailRate !== nextState.showFailRate && nextState.showFailRate === false)
		{
			this.fetchCourses([nextState.courses[0].code]);
		}

		return nextState.courses !== this.state.courses
			|| nextState.showFailRate !== this.state.showFailRate
			|| nextState.failedLoading !== this.state.failedLoading;
	}

	componentWillReceiveProps(nextProps)
	{
		// codes should be unique as user is redirected on duplicates
		this.fetchCourses(nextProps.codes);
	}

	arrayReduceSum(total, num)
	{
		return total + num;
	}

	arrayAverage(arr)
	{
		return arr.reduce(this.arrayReduceSum, 0) / arr.length;
	}

	prepareAvgData()
	{
		// start out by computing the average amounts amount of the different grades
		var avgFail = Math.round(this.arrayAverage(this.state.courses[0].datasets[0].data));
		var avgThree = Math.round(this.arrayAverage(this.state.courses[0].datasets[1].data));
		var avgFour = Math.round(this.arrayAverage(this.state.courses[0].datasets[2].data));
		var avgFive = Math.round(this.arrayAverage(this.state.courses[0].datasets[3].data));

		const avgData =
			{
				labels: ["U", "3", "4", "5"],
				datasets: [
					{
						data: [avgFail, avgThree, avgFour, avgFive],
						backgroundColor: [colors.failures, colors.threes, colors.fours, colors.fives],
					}
				],
			};
		return avgData;
	}

	coursesCallback(fetchedCourses)
	{
		if(this.state.failedLoading)
		{
			return;
		}

		var courses = new Array(fetchedCourses.length);
		var rates   = new Array(fetchedCourses.length);

		for(var i = 0; i < fetchedCourses.length; ++i)
		{
			// use to get latest name for course
			var lastIndex = fetchedCourses[i].length - 1;
			courses[i] =
				{
					code: fetchedCourses[i][0].code,
					name: fetchedCourses[i][lastIndex].name,
					exams: [],
					solutions: [],
					labels: [],
					datasets:
					[
						{
							label: "U",
							backgroundColor: colors.failures,
							borderWidth: 0,
							data: [],
						},
						{
							label: "3",
							backgroundColor: colors.threes,
							borderWidth: 0,
							data: [],
						},
						{
							label: "4",
							backgroundColor: colors.fours,
							borderWidth: 0,
							data: [],
						},
						{
							label: "5",
							backgroundColor: colors.fives,
							borderWidth: 0,
							data: [],
						},
					],
				};

			rates[i] =
				{
					labels: [],
					datasets:
					[
						{
							label: "U",
							backgroundColor: colors.failures,
							borderColor: colors.failures,
							data: [],
							fill: false,
						},
						{
							label: "3",
							backgroundColor: colors.threes,
							borderColor: colors.threes,
							data: [],
							fill: false,
						},
						{
							label: "4",
							backgroundColor: colors.fours,
							borderColor: colors.fours,
							data: [],
							fill: false,
						},
						{
							label: "5",
							backgroundColor: colors.fives,
							borderColor: colors.fives,
							data: [],
							fill: false,
						},
					], };

			for(var j = 0; j < fetchedCourses[i].length; ++j)
			{
				var failed = fetchedCourses[i][j].failures;
				var threes = fetchedCourses[i][j].threes;
				var fours  = fetchedCourses[i][j].fours;
				var fives  = fetchedCourses[i][j].fives;

				var taken    = fetchedCourses[i][j].taken
				var total    = failed+threes+fours+fives;
				var exam     = fetchedCourses[i][j].exam;
				var solution = fetchedCourses[i][j].solution;

				courses[i].exams.push({[taken]: exam});
				courses[i].solutions.push({[taken]: solution});
				courses[i].labels.push(taken);
				courses[i].datasets[0].data.push(failed);
				courses[i].datasets[1].data.push(threes);
				courses[i].datasets[2].data.push(fours);
				courses[i].datasets[3].data.push(fives);

				rates[i].labels.push(taken);
				rates[i].datasets[0].data.push(Math.round(failed / total * 100));
				rates[i].datasets[1].data.push(Math.round(threes / total * 100));
				rates[i].datasets[2].data.push(Math.round(fours / total * 100));
				rates[i].datasets[3].data.push(Math.round(fives / total * 100));
			}
		}

		this.setState(
			{
				adjustedFailure: this.computeAdjustedFailure(courses[0]),
				loaded: true,
				courses: courses,
				rates: rates,
				panelData: // resets panel data so that data from old query isn't kept
				{
					taken:        null,
					examLink:     null,
					solutionLink: null,
					labels:       [],
					datasets:     [],
				},
				selectedData:
				{
					taken:        null,
					examLink:     null,
					solutionLink: null,
					labels:       [],
					datasets:     [],
				},
			});
	}

	async fetchCourse(course)
	{
		const resp = await fetch(process.env.REACT_APP_SERVER_URL + "courses/" + course);
		var respJSON = await resp.json();
		if ("error" in respJSON)
		{
			this.setState({failedLoading: true});
		}

		return respJSON;
	}

	// return single promise for array of courses
	async fetchCourses(codes)
	{
		const pCourses = codes.map(this.fetchCourse);
		const courses  = await Promise.all(pCourses);
		this.coursesCallback(courses);
	}

	updateExamPanel(tooltipModel)
	{
		if(tooltipModel.dataPoints != null)
		{
			var examCourse = this.state.courses[0];
			var exam = examCourse.exams.find((entry) =>
				{
					return tooltipModel.title in entry;
				});
			var solution = examCourse.solutions.find((entry) =>
				{
					return tooltipModel.title in entry;
				});
			var examLink = exam[tooltipModel.title];
			var solutionLink = solution[tooltipModel.title];
			var newData = tooltipModel.dataPoints.map(point => (parseInt(point.value)));

			var backgroundColor;
			var selectedData = this.state.selectedData.datasets;

			if(selectedData.length !== 0 && JSON.stringify(selectedData[0].data) === JSON.stringify(newData))
			{
				backgroundColor = [colors.failures, colors.threes, colors.fours, colors.fives];
			}
			else
			{
				backgroundColor = Array(4).fill("grey");
			}

			var panelData =
				{
					taken: tooltipModel.title[0],
					examLink: examLink,
					solutionLink: solutionLink,
					labels: ["U", "3", "4", "5"],
					datasets: [
						{
							data: newData,
							backgroundColor: backgroundColor,
						}
					],
				};

			this.setState(
				{
					panelData: panelData,
				});
			this.examPanelElement.current.changeData(panelData);
		}
	}

	selectData()
	{
		var newSelectedData =
			{
				taken: this.state.panelData.taken,
				examLink: this.state.panelData.examLink,
				solutionLink: this.state.panelData.solutionLink,
				labels: ["U", "3", "4", "5"],
				datasets:[
					{
						data: this.state.panelData.datasets[0].data,
						backgroundColor: [colors.failures, colors.threes, colors.fours, colors.fives],
					}
				],
			};
		this.setState(
			{
				selectedData: newSelectedData,
			});
		this.examPanelElement.current.changeData(newSelectedData);
	}

	// triggered on mouse leaving chart canvas
	// used to restore exam panel to last clicked exam
	resetExamPanel()
	{
		if(this.state.selectedData.datasets.length === 0)
		{
			this.examPanelElement.current.showAverage();
		}
		else
		{
			this.examPanelElement.current.changeData(this.state.selectedData);
		}
	}

	// compute JSON with grade rate fields
	computeGradeRates(course)
	{
		var failures = course.datasets[0].data.reduce(this.sumAccumulate);
		var threes   = course.datasets[1].data.reduce(this.sumAccumulate);
		var fours    = course.datasets[2].data.reduce(this.sumAccumulate);
		var fives    = course.datasets[3].data.reduce(this.sumAccumulate);
		var total    = failures + threes + fours + fives;

		return {
			failures: Math.round(failures / total * 100),
			threes:   Math.round(threes / total * 100),
			fours:    Math.round(fours / total * 100),
			fives:    Math.round(fives / total * 100),
		};
	}

	sumAccumulate(partial_sum, a)
	{
		return partial_sum + a;
	}

	// compute the adjusted failure by taking the most
	// attended exam in the past year, and computing
	// the two previous years results from that date
	computeAdjustedFailure(course)
	{
		var lastIndex = course.labels.length - 1;
		var lowerBound  = new Date(course.labels[lastIndex]);
		lowerBound.setFullYear(lowerBound.getFullYear() - 1);

		// add month to account for varying exam dates
		lowerBound.setMonth(lowerBound.getMonth() + 1);

		// find major exam date
		var majorIndex = lastIndex;
		var largestSum = course.datasets[0].data[lastIndex]
			+ course.datasets[1].data[lastIndex]
			+ course.datasets[2].data[lastIndex]
			+ course.datasets[3].data[lastIndex];

		// index and date reused for other loop
		var i;
		var date;
		for(i = lastIndex; i >= 0; --i)
		{
			date = new Date(course.labels[i]);
			if(date < lowerBound)
			{
				break;
			}
			var sum = course.datasets[0].data[i]
				+ course.datasets[1].data[i]
				+ course.datasets[2].data[i]
				+ course.datasets[3].data[i];

			if(sum > largestSum)
			{
				majorIndex = i;
			}
		}

		var majorFailRates = [];

		var upper = new Date(course.labels[majorIndex]);
		upper.setMonth(upper.getMonth() + 1);
		var lower = new Date(course.labels[majorIndex]);
		lower.setMonth(lower.getMonth() - 1);

		for(i = majorIndex; i >= 0; --i)
		{
			if(majorFailRates.length >= 3)
				break;

			date = new Date(course.labels[i]);

			// date was between boundaries
			if(date < upper && date >= lower)
			{
				var failures = course.datasets[0].data[i];
				var total    = failures
					+ course.datasets[1].data[i]
					+ course.datasets[2].data[i]
					+ course.datasets[3].data[i];
				var failRate = Math.round(failures / total * 100);
				majorFailRates.unshift(failRate);

				// update boundaries
				upper.setFullYear(upper.getFullYear() - 1);
				lower.setFullYear(lower.getFullYear() - 1);
			}
		}

		// finally compute average of the rates
		return Math.round(majorFailRates.reduce(this.sumAccumulate) / majorFailRates.length);
	}

	renderCourseFromList(course)
	{
		var rates = this.computeGradeRates(course);
		var adjusted = this.computeAdjustedFailure(course);

		return(
			<tr key={course.code}>
				<th scope="row">{course.code}</th>
				<td>{rates.failures}%</td>
				<td>{rates.threes}%</td>
				<td>{rates.fours}%</td>
				<td>{rates.fives}%</td>
				<td>{adjusted}%</td>
			</tr>
		);
	}

	toggleFailRate()
	{
		this.setState({ showFailRate: !this.state.showFailRate })
	}

	render()
	{
		if(this.state.failedLoading)
		{
			return(
				<div
					data-testid="failed-loading"
					className="mx-auto">
				<p>Failed loading course</p>
			</div>
			);
		}

		if(!this.state.loaded)
		{
			return(<div data-testid="loading"
				className="mx-auto spinner-border" />);
		}

		if(this.state.courses.length > 1)
		{
			return(
				<Col xs={12} lg={8} className="mx-auto">
					<Table responsive bordered hover
						style={{ borderColor: colors.threes }}>
					<thead>
						<tr>
							<th>Course code</th>
							<th>U</th>
							<th>3</th>
							<th>4</th>
							<th>5</th>
							<th>
									Adjusted fail rate
								<FontAwesomeIcon
									icon="question-circle"
									data-toggle="tooltip"
									title="Last three non-reexams averaged"/>
							</th>
						</tr>
					</thead>
					<tbody>
							{this.state.courses.map(this.renderCourseFromList)}
					</tbody>
				</Table>
			</Col>
			);
		}

		return (
			<Col xs={12}>
				<Row className="flex-row-reverse mx-auto">
					<Col xs={12} md={3} className="mx-auto">
						<ExamPanel data={this.state.courses[0]}
							averageData={this.prepareAvgData()}
							ref={this.examPanelElement}
							code={this.state.courses[0].code}
							exam={this.state.courses[0].exam}
							overallRate={this.state.adjustedFailure}/>
					</Col>
					<Col xs={12} md={9} className="mx-auto">
						<div className="overview">
							<Row>
								<Col xs={9}>
									<h4>[{this.state.courses[0].code}] - {this.state.courses[0].name}</h4>
								</Col>
								<Col xs={2} className="align-self-end">
									<div className="custom-control custom-switch text-right">
											<input type="checkbox" 
													className="custom-control-input" 
													onChange={this.toggleFailRate} 
													id="fail-rate-toggle"
													data-testid="fail-rate-toggle"/>
										<label className="custom-control-label" htmlFor="fail-rate-toggle">Rates</label>
									</div>
								</Col>
							</Row>
							<div
								className="h-100"
								data-testid="chart-container"
								onClick={this.selectData}
								onTouchEnd={this.selectData}
								onMouseOut={this.resetExamPanel}>
								{this.state.showFailRate ?
									<Line
										key={this.state.courses[0].code}
										data={this.state.rates[0]}
										options=
										{{
											maintainAspectRatio: false,
											legend:
											{
												display: true,
												position: "bottom",
											},
											tooltips:
											{
												enabled: false,
												mode: "label",
												intersect: false,
												custom: this.updateExamPanel.bind(this),
											},
											hover:
											{
												intersect: false,
											},
										}}
									/>
									:
									<Bar key={this.state.courses[0].code}
										data={this.state.courses[0]}
										options=
										{{
											maintainAspectRatio: false,
											legend:
											{
												display: true,
												position: "bottom",
											},
											tooltips:
											{
												enabled: false,
												mode: "label",
												intersect: false,
												custom: this.updateExamPanel.bind(this),
											},
											hover:
											{
												intersect: false,
											},
										}}
									/>
								}
								</div>
							</div>
						</Col>
					</Row>
				</Col>
		);
	}
}

export default ExamAnalytics;
