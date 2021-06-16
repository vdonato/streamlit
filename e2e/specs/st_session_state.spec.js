/**
 * @license
 * Copyright 2018-2021 Streamlit Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

describe("st.beta_session_state", () => {
  beforeEach(() => {
    cy.visit("http://localhost:3000/");

    // Make the ribbon decoration line disappear
    cy.get("[data-testid='stDecoration']").invoke("css", "display", "none");
  });

  it("has correct starting values", () => {
    cy.get(".stMarkdown").contains("item_counter: 0");
    cy.get(".stMarkdown").contains("attr_counter: 0");
    // item_counter + attr_counter + initialized flag
    cy.get(".stMarkdown").contains("len(st.session_state): 3");
  });

  it("can get/set/delete session_state items", () => {
    cy.get(".stMarkdown").contains("item_counter: 0");
    cy.get(".stMarkdown").contains("attr_counter: 0");

    cy.get(".stButton button")
      .contains("inc_item_counter")
      .click();
    cy.get(".stMarkdown").contains("item_counter: 1");
    cy.get(".stMarkdown").contains("attr_counter: 0");

    cy.get(".stButton button")
      .contains("inc_item_counter")
      .click();
    cy.get(".stMarkdown").contains("item_counter: 2");
    cy.get(".stMarkdown").contains("attr_counter: 0");

    cy.get(".stButton button")
      .contains("del_item_counter")
      .click();
    cy.get(".stMarkdown")
      .contains("item_counter:")
      .should("not.exist");
    cy.get(".stMarkdown").contains("attr_counter: 0");
    cy.get(".stMarkdown").contains("len(st.session_state): 2");
  });

  it("can get/set/delete session_state attrs", () => {
    cy.get(".stMarkdown").contains("item_counter: 0");
    cy.get(".stMarkdown").contains("attr_counter: 0");

    cy.get(".stButton button")
      .contains("inc_attr_counter")
      .click();
    cy.get(".stMarkdown").contains("item_counter: 0");
    cy.get(".stMarkdown").contains("attr_counter: 1");

    cy.get(".stButton button")
      .contains("inc_attr_counter")
      .click();
    cy.get(".stMarkdown").contains("item_counter: 0");
    cy.get(".stMarkdown").contains("attr_counter: 2");

    cy.get(".stButton button")
      .contains("del_attr_counter")
      .click();
    cy.get(".stMarkdown").contains("item_counter: 0");
    cy.get(".stMarkdown")
      .contains("attr_counter:")
      .should("not.exist");
    cy.get(".stMarkdown").contains("len(st.session_state): 2");
  });
});
