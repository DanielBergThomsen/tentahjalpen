import React, { Component } from "react";
import
{
	Route,
	HashRouter,
	Link
} from "react-router-dom";

import
{
	Container,
	Row,
	Col,
} from "react-bootstrap";

import HomePage      from "./components/HomePage";
import SearchBar     from "./components/SearchBar";
import ExamAnalytics from "./components/ExamAnalytics";

import logo from "./art/with-text.svg";
import "./styles/logo.css";

import ReactGA from "react-ga";


class Main extends Component
{
	constructor(props)
	{
		super(props);
		this.routerRef = React.createRef();

		// initialize GA tracking
		ReactGA.initialize(process.env.REACT_APP_TRACKING_ID);

		// hopefully make GDPR compliant
		ReactGA.set({ anonymizeIp: true });
		ReactGA.pageview(window.location.pathname + window.location.search);
	}

	render() {
		return (
			<HashRouter ref={this.routerRef}>
				<div>
					<Container>
						<Row>
							<Col xs={12} md={8} className="mt-5 mb-3 mx-auto">
								<Link to="/">
									<img src={logo} alt="" className="img-fluid" />
								</Link>
							</Col>
						</Row>
						<Row>
							<Col xs={12} md={8} className="mx-auto mb-5">
								<SearchBar onSubmission={this.fetchAndDisplay}
									routerRef={this.routerRef}/>
							</Col>
						</Row>
					</Container>
					<Container fluid={true}>
						<Row className="content">
							<Route exact path="/" component={HomePage} />
							<Route path="/statistics/:exam+"
								exact render={(props) =>
										<ExamAnalytics
											codes={props.match.params.exam.split("/")}
										/>} />
										</Row>
									</Container>
								</div>
							</HashRouter>
		);
	}
}

export default Main;
