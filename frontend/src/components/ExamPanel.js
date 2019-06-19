import React, {Component} from "react";
import
{
	Pie,
} from "react-chartjs-2";

import
{
	Button,
	Modal,
	Row,
	Col,
} from "react-bootstrap";

import "../styles/exam_analytics.css";

class ExamPanel extends Component
{
	constructor(props)
	{
		super(props);

		this.state = {
			showModal:    false,
			taken:        "",
			showAverage:  true,
			total:        0,
			failRate:     0,
			threesRate:   0,
			foursRate:    0,
			fivesRate:    0,
			data:         [],
			examLink:     null,
			solutionLink: null,
		};

		this.averageRates = this.computeGradeRate(this.props.averageData);
		this.chartRef = React.createRef();
		this.uploadExam = this.uploadExam.bind(this);
		this.showModal = this.showModal.bind(this);
		this.showAverage = this.showAverage.bind(this);
		this.hideModal = this.hideModal.bind(this);
	}


	componentDidUpdate(prevProps)
	{

		// dirty hack to ensure pie chart respects dimensions of
		// other components in panel
		// this is necessary as resizing in chartjs is only
		// triggered on window resize events
		if(this.chartRef.current != null)
		{
			const chart = this.chartRef.current.chartInstance;
			if(chart != null && chart !== undefined)
			{
				chart.resize();
			}
		}
	}

	uploadExam(event)
	{
		var file = event.target.files[0];
		var reader = new FileReader();
		var encoded = "";

		reader.onload = function(readerEvt) {
			var binaryString = readerEvt.target.result;
			encoded = btoa(binaryString);
			var suggestion =
				{
					exam:  encoded
				};
			var url = process.env.REACT_APP_SERVER_URL + "courses/" + this.props.code + "/" + this.state.data.taken + "/exam";
			fetch(url,{
				method: "PUT",
				mode: "cors",
				cache: "no-cache",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(suggestion),
			})
				.then(this.showModal)
				.catch(error => alert("Something went wrong"));
		}.bind(this);

		reader.readAsBinaryString(file);
	}

	showModal()
	{
		this.setState(
			{
				showModal: true,
			}
		);
	}

	hideModal()
	{
		this.setState(
			{
				showModal: false,
			}
		);
	}

	showAverage()
	{
		this.setState(
			{
				showAverage: true,
			});
	}

	changeData(newData)
	{
		var rates = this.computeGradeRate(newData);
		this.setState(
			{
				showAverage: false,
				total:       rates.total,
				failRate:    rates.failRate,
				threesRate:  rates.threeRate,
				foursRate:   rates.fourRate,
				fivesRate:   rates.fiveRate,
				data:        newData,
			}
		);
	}

	computeGradeRate(data)
	{
		var gradesData = data.datasets[0].data;
		var failures   = gradesData[0];
		var threes     = gradesData[1];
		var fours      = gradesData[2];
		var fives      = gradesData[3];
		var total      = failures + threes + fours + fives;

		return {
			total:     total,
			failRate:  Math.round(100*(failures/total)),
			threeRate: Math.round(100*(threes/total)),
			fourRate:  Math.round(100*(fours/total)),
			fiveRate:  Math.round(100*(fives/total)),
		};

	}

	render()
	{
		if(this.state.showAverage)
		{
			return(
				<div className="d-flex flex-column align-items-stretch overview">
					<div className="flex-grow-1 pie">
						<Pie
							ref={this.chartRef}
							data-testid="chart"
							width={1} height={1}
							data={this.props.averageData}
							options={{
								maintainAspectRatio: false,
								responsive: true,
								tooltips:
								{
									bodyAlign:       'center',
									footerAlign:     'center',
									backgroundColor: "white",
									bodyFontSize:     15,
									bodyFontStyle:   "bold",
									footerFontSize:   12,
									footerFontStyle: "normal",
									footerFontColor: "black",
									displayColors:    false,
									callbacks:
									{
										label: function(tooltipItem, data)
										{
											return data.labels[tooltipItem.index];
										},

										footer: function(tooltipItem, data)
										{
											return data.datasets[0].data[tooltipItem[0].index];
										},

										afterFooter: function(tooltipItem, data)
										{
											var dataset = data.datasets[0];
											var total   = dataset.data.reduce((total, num) => total + num);

											var percent = Math.round(dataset.data[tooltipItem[0].index] / total * 100);
											return '(' + percent + '%)';
										},

										labelTextColor: function(tooltipItem, chart)
										{
											var dataset = chart.config.data.datasets[tooltipItem.datasetIndex];
											return dataset.backgroundColor[tooltipItem.index];
										},
									}
								},
								legend:
								{
									display: false,
								},
							}}/>
					</div>

					<div className="mt-2">
						<div><span className="text-primary">Averages</span></div>
						<div><span>Adjusted fail-rate: {this.props.overallRate}%</span></div>
						<div><span>Failures: {this.averageRates.failRate}%</span></div>
						<div><span>Threes: {this.averageRates.threeRate}%</span></div>
						<div><span>Fours: {this.averageRates.fourRate}%</span></div>
						<div><span>Fives: {this.averageRates.fiveRate}%</span></div>
					</div>

				</div>
			);
		}

		return (
			<div className="d-flex flex-column align-items-stretch overview">
				<Modal show={this.state.showModal} onHide={this.hideModal}>
					<Modal.Header closeButton>
						<Modal.Title>You're awesome</Modal.Title>
					</Modal.Header>
					<Modal.Body>
							Thank you so much for your contribution!
							If it were possible, I'd hug you right now!
					</Modal.Body>
					<Modal.Footer>
						<Button variant="primary" onClick={this.hideModal}>
								You're welcome!
						</Button>
					</Modal.Footer>
				</Modal>
				<div className="flex-grow-1 pie">
					<Pie
						ref={this.chartRef}
						data-testid="chart"
						width={1} height={1}
						data={this.state.data}
						options={{
							maintainAspectRatio: false,
							responsive: true,
							tooltips:
							{
								bodyAlign:       'center',
								footerAlign:     'center',
								backgroundColor: "white",
								bodyFontSize:     15,
								bodyFontStyle:   "bold",
								footerFontSize:   12,
								footerFontStyle: "normal",
								footerFontColor: "black",
								displayColors:    false,
								callbacks:
								{
									label: function(tooltipItem, data)
									{
										return data.labels[tooltipItem.index];
									},

									footer: function(tooltipItem, data)
									{
										return data.datasets[0].data[tooltipItem[0].index];
									},

									afterFooter: function(tooltipItem, data)
									{
										var dataset = data.datasets[0];
										var total   = this.state.total;

										var percent = Math.round(dataset.data[tooltipItem[0].index] / total * 100);
										return '(' + percent + '%)';
									}.bind(this),

									labelTextColor: function(tooltipItem, chart)
									{
										var dataset = chart.config.data.datasets[tooltipItem.datasetIndex];
										return dataset.backgroundColor[tooltipItem.index];
									},
								}
							},
							legend:
							{
								display: false,
							},
						}}/>
				</div>

				<div className="mt-2">
					<div><span>Adjusted fail-rate: {this.props.overallRate}%</span></div>
					<div><span>Failures: {this.state.failRate}%</span></div>
					<div><span>Threes: {this.state.threesRate}%</span></div>
					<Row>
						<Col xs={7}>
							<div><span>Fours: {this.state.foursRate}%</span></div>
							<div><span>Fives: {this.state.fivesRate}%</span></div>
						</Col>
						<Col xs={5} className="align-self-end">
							<Button onClick={this.showAverage} size="sm"
								variant="outline-primary">Averages</Button>
						</Col>
					</Row>
					<div className="upload_buttons mt-2 mx-auto text-center">
							{this.state.data.examLink != null ?
									<label className="btn btn-block btn-outline-primary invisible">
										<a
											className="visible"
											href={this.state.data.examLink}
											target="_blank"
											rel="noopener noreferrer">
											View the damage
									</a>
								</label>
									:
									<label className="btn btn-block btn-outline-primary">
											Upload exam <input type="file" onChange={this.uploadExam} hidden />
										</label>
							}
											{this.state.data.solutionLink != null ?
													<label className="btn btn-block btn-outline-primary invisible">
														<a
															className="visible"
															href={this.state.data.solutionLink}
															target="_blank"
															rel="noopener noreferrer">
															Let me cheat
													</a>
												</label>
													:
													<label className="btn btn-outline-primary">
															Upload solution <input type="file" onChange={this.uploadExam} hidden />
														</label>
											}
													</div>
												</div>

											</div>
		);
	}
}

export default ExamPanel;
