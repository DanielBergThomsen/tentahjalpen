import React from "react";

import { render, fireEvent } from "react-testing-library";
import SearchBar from "./SearchBar";

const setupInput = () => {
	const utils = render(<SearchBar />);
	const inputField = utils.getByTestId("input");
	return {inputField, utils};
};

const giveInput = (inputField, input) => {
	fireEvent.change(inputField, {target: {value: input}});
};

describe("Search bar component", () => {
	beforeEach(() => {
		fetch.resetMocks();
		fetch.mockResponseOnce(JSON.stringify(Array(15).fill(
			{
				"code": "EDA322",
				"name": "Digital Konstruktion",
				"uri":  "http://example.com"
			}
		)));

	});
	test("allows user input", () => {
		const {inputField,} = setupInput();
		const input = "test";
		giveInput(inputField, input);
		expect(inputField.value).toBe(input);
	});

	test("shows suggestions when given input", async () => {
		const {inputField, utils} = setupInput();
		const input = "e";
		giveInput(inputField, input);
		expect(utils.queryByText("[EDA322] Digital Konstruktion")).not.toBeNull();
	});

	test("don't show suggestions when not given input", async () => {
		const {inputField, utils} = setupInput();
		giveInput(inputField, "");
		expect(utils.queryByText("[EDA322] Digital Konstruktion")).toBeNull();
		const input = "e";
		giveInput(inputField, input);
		expect(utils.queryByText("[EDA322] Digital Konstruktion")).not.toBeNull();
		giveInput(inputField, "");
		expect(utils.queryByText("[EDA322] Digital Konstruktion")).toBeNull();
	});

	test("don't show too many suggestions", async () => {
		const {inputField, utils} = setupInput();
		const input = "e";
		giveInput(inputField, input);
		console.log();
		expect(utils.queryAllByText("[EDA322] Digital Konstruktion").length).toBe(15);
	});

	test("don't show suggestions when input broken by seperator", async () => {
		const {inputField, utils} = setupInput();
		const input = "e ";
		giveInput(inputField, input);
		expect(utils.queryByText("[EDA322] Digital Konstruktion")).toBeNull();
		giveInput(inputField, "e e");
		expect(utils.queryByText("[EDA322] Digital Konstruktion")).not.toBeNull();
	});
});
