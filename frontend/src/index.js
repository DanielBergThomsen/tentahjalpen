import React from "react";
import ReactDOM from "react-dom";
import Main from "./Main";

import "./styles/custom.scss";
import "./styles/index.css";

import WebFont from 'webfontloader';

import { library }      from "@fortawesome/fontawesome-svg-core";
import { faQuestionCircle, faSearch } from "@fortawesome/free-solid-svg-icons";

library.add(faQuestionCircle);
library.add(faSearch);

WebFont.load({
	google: {
		families: ["Montserrat:500,800", "sans-serif"]
	}
});

ReactDOM.render(
	<Main/>,
	document.getElementById("root")
);
