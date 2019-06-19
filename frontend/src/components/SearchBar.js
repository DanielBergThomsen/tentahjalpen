import React, { Component } from "react";

import
{
	Button,
	InputGroup,
	FormControl,
	Dropdown,
} from "react-bootstrap";

import colors from "../styles/colors.json";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import "../styles/search_bar.css";
import "../styles/dropdown_custom.css";

class SearchBar extends Component
{

	constructor(props)
	{
		super(props);

		this.state =
			{
				hideSuggestions: false, // boolean required for onBlur logic
				suggestions: [],
				input: "",
			};
		this.codes = []

		this.search = this.search.bind(this);
		this.autoComplete = this.autoComplete.bind(this);
		this.renderSuggestion = this.renderSuggestion.bind(this);
		this.requestData = this.requestData.bind(this);
		this.fetchAndDisplay = this.fetchAndDisplay.bind(this);
		this.handleKeyPress = this.handleKeyPress.bind(this);
		this.handleBlur = this.handleBlur.bind(this);

		// create ref to input form so focus can be retained
		// when using autocomplete feature
		this.inputRef = React.createRef();
	}

	componentDidMount()
	{
		this.fetchCourseCodes();
	}

	async fetchCourseCodes()
	{
		const resp = await fetch(process.env.REACT_APP_SERVER_URL + "courses");
		this.codes = await resp.json();
	}

	fetchAndDisplay(codes)
	{
		var uniqueCodes = new Set(codes);
		var fetchCodes  = this.codes.filter((entry) =>
			{
				return uniqueCodes.has(entry.code);
			}
		);
		fetchCodes = fetchCodes.map((entry) =>
			{
				return entry.code;
			})

		var params = fetchCodes.join("/");
		this.props.routerRef.current.history.push("/statistics/" + params);
	}


	// return words in space-seperated string
	parseInput(string, removeEmpty)
	{
		if(string.length <= 0)
			return [];
		else
		{
			var parsed = string.toUpperCase().split(" ");

			// remove empty string
			if(removeEmpty && parsed[parsed.length - 1] === "")
				parsed.pop();

			return parsed;
		}
	}

	search(event)
	{
		var newInput = event.target.value;
		var parsed   = this.parseInput(newInput);

		if(parsed.length <= 0)
		{
			this.setState(
				{
					hideSuggestions: false,
					suggestions: [],
					input: newInput,
				});
			return;
		}

		// extract last word in parsed input
		var searchString = parsed[parsed.length - 1];

		if(typeof this.codes === "undefined" || searchString === "")
		{
			this.setState(
				{
					hideSuggestions: false,
					suggestions: [],
					input: newInput,
				});
			return;
		}

		var newSuggestions = [];

		// for every code, but cap at fifteen
		for(var i = 0; i < this.codes.length && newSuggestions.length < 15; ++i)
		{
			var course = this.codes[i];
			var code = course.code.toUpperCase();
			var name = course.name.toUpperCase();
			if(code.startsWith(searchString)
				|| name.startsWith(searchString))
				newSuggestions.push(course);
		}

		this.setState(
			{
				hideSuggestions: false,
				suggestions: newSuggestions,
				input: newInput,
			});
	}

	// add code to searchbar when suggestion is chosen
	autoComplete(code)
	{
		var input  = this.state.input.toUpperCase();
		var parsed = this.parseInput(input, false);
		var regex = new RegExp(parsed[parsed.length - 1] + "$");

		var newInput = input.replace(regex, code) + " ";
		this.setState(
			{
				shouldRemoveSuggestions: false,
				suggestions: [],
				input: newInput,
			});

		// regain focus in input component
		this.inputRef.current.focus();

		this.requestData(newInput);
	}

	requestData(input)
	{
		this.fetchAndDisplay(this.parseInput(input, true))
	}

	handleKeyPress(event)
	{
		if(event.key === "Enter")
		{
			this.requestData(this.state.input);
		}
	}

	handleBlur()
	{
		this.setState(
			{
				hideSuggestions: true,
			}
		);
	}

	renderSuggestion(suggestion)
	{
		return(
			<Dropdown.Item
				className="dropdown-item dropdown_custom"
				key={suggestion.code}
				onMouseDown={() => this.autoComplete(suggestion.code)}>
			<span>[{suggestion.code}] {suggestion.name}</span>
		</Dropdown.Item>
		);
	}

	render()
	{
		return(
			<div>
				<InputGroup className="input">
					<FormControl
						data-testid="input"
						size="lg"
						style={{ borderColor: colors.threes }}
						placeholder="Course codes..."
						onChange={this.search}
						onKeyPress={this.handleKeyPress}
						onBlur={this.handleBlur}
						value={this.state.input}
						ref={this.inputRef}
						autoFocus/>
						{!this.state.hideSuggestions && this.state.suggestions.length > 0 &&
								<Dropdown.Menu show
									data-testid="suggestions"
									className="w-100 mx-auto">
									{this.state.suggestions.map(this.renderSuggestion)}
								</Dropdown.Menu>}
								<InputGroup.Append>
									<Button
										variant="outline-primary"
													onClick={() => this.requestData(this.state.input)}>
									<FontAwesomeIcon icon="search"/>
								</Button>
							</InputGroup.Append>
						</InputGroup>
					</div>
		);
	}
}

export default SearchBar;
