describe("search bar component", () => {

	beforeEach(() => {
		cy.visit("http://localhost:3000");
		cy.get("input").click();
	});

	it("doesn't give any suggestions when nothing matches query", () => {
		cy.focused()
			.type("TEST123");
		cy.get(".dropdown-menu")
			.should("not.be.visible");
	});

	it("shows exam overview after clicking search button", () => {
		cy.focused()
			.type("EDA322");
		cy.get("input")
			.get("button")
			.click();

		cy.get(".content")
			.should("be.visible");
	});

	it("shows exam overview after clicking search suggestion", () => {
		cy.focused()
			.type("EDA32"); // as in EDA322
		cy.get(".dropdown-menu")
			.contains("EDA322")
			.click();

		cy.get(".content")
			.should("be.visible");
	});

	it("shows search results", () => {
		cy.focused()
			.type("EDA32"); // as in EDA322
		cy.get(".dropdown-menu")
			.contains("EDA322")
			.should("be.visible");
	});

});

describe("exam page overview", () => {

	beforeEach(() => {
		cy.visit("http://localhost:3000");
		cy.get("input").click();
		cy.focused()
			.type("EDA32");
		cy.get(".dropdown-menu")
			.contains("EDA322")
			.click();
	});


	var assertNumberOnString = (string) =>
	{
		cy.get(".content")
			.contains(string)
			.invoke("text")
			.then((text) => {
				const num = parseInt(text.replace(string, "")
					.replace("%", ""));
				expect(num).to.be.a("number");
			});
	};


	it("shows valid numbers as exam averages when course is searched for", () => {

		assertNumberOnString("Adjusted fail-rate: ");
		assertNumberOnString("Failures: ");
		assertNumberOnString("Threes: ");
		assertNumberOnString("Fours: ");
		assertNumberOnString("Fives: ");
	});

	it("shows us a canvas component (exams over time)", () => {
		cy.get("[data-testid=chart-container]")
			.get("canvas")
			.should("be.visible");
	});

	it("shows us a canvas component (rates over time)", () => {
		cy.get("[data-testid=fail-rate-toggle]")
			.click({force: true});
		cy.get("[data-testid=chart-container]")
			.get("canvas")
			.should("be.visible");
	});


	it("shows us a canvas (pie chart)", () => {
		cy.get("[data-testid=pie-chart-container]")
			.get("canvas")
			.should("be.visible");
	});
});

describe("url navigation", () => {

	it("can access courses by directly entering their url", () => {
		cy.visit("http://localhost:3000/#/statistics/EDA322");
		cy.get(".content")
			.should("be.visible");
	});
});


