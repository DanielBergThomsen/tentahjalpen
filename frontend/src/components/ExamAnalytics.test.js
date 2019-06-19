import React from "react";

import { render, fireEvent } from "react-testing-library";
import ExamAnalytics from "./ExamAnalytics";

function setup_comp(codes)
{
	return render(<ExamAnalytics codes={codes} />);
};

const config_one = JSON.stringify(
	[
		{
			"taken": "2017-03-01",
			"failures": 5,
			"threes": 5,
			"fours": 5,
			"fives": 5,
			"code": "EDA322",
			"name": "Digital Konstruktion",
			"exam":  null,
			"solution":  null,
		},
		{
			"taken": "2018-03-14",
			"failures": 5,
			"threes": 5,
			"fours": 5,
			"fives": 5,
			"code": "EDA322",
			"name": "Digital Konstruktion",
			"exam":  "http://example.com/exam",
			"solution":  null,
		},
		{
			"taken": "2019-01-09",
			"failures": 5,
			"threes": 5,
			"fours": 5,
			"fives": 5,
			"code": "EDA322",
			"name": "Digital Konstruktion",
			"exam":  null,
			"solution":  "http://example.com/solution",
		},
		{
			"taken": "2019-03-08",
			"failures": 25,
			"threes": 5,
			"fours": 5,
			"fives": 5,
			"code": "EDA322",
			"name": "Digital Konstruktion",
			"exam":  "http://example.com/exam",
			"solution":  "http://example.com/solution",
		},
	]);

const config_fail = JSON.stringify({error: "Not found"});

describe("Exam analytics component", () =>
	{
		beforeEach(() =>
			{
				fetch.resetMocks();
			});

		test("shows user loading circle while awaiting data", () =>
			{
				fetch.mockResponseOnce(config_one);
				const comp = setup_comp(["EDA322"]);
				expect(comp.getByTestId("loading")).not.toBeNull();
			});

		test("shows message when unable to load data", async () =>
			{
				fetch.mockResponseOnce(config_fail);
				const comp = setup_comp(["EDA322"]);
				expect(await comp.findByTestId("failed-loading")).not.toBeNull();
			});

		test("displays proper average grade rates", async () =>
			{
				fetch.mockResponseOnce(config_one);
				const comp = setup_comp(["EDA322"]);

				// need to await processing of data (loading circle is shown to user)
				expect(await comp.findByText("Failures: 40%")).not.toBeNull();
				expect(comp.queryByText("Threes: 20%")).not.toBeNull();
				expect(comp.queryByText("Fours: 20%")).not.toBeNull();
				expect(comp.queryByText("Fives: 20%")).not.toBeNull();
			});

		test("computes the adjusted grade properly", async () =>
			{
				fetch.mockResponseOnce(config_one);
				const comp = setup_comp(["EDA322"]);
				expect(await comp.findByText("Adjusted fail-rate: 38%")).not.toBeNull();
			});
	});
