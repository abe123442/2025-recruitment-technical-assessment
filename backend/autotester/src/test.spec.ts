const request = require("supertest");

describe("Task 1", () => {
  describe("POST /parse", () => {
    const getTask1 = async (inputStr) => {
      return await request("http://localhost:8080")
        .post("/parse")
        .send({ input: inputStr });
    };

    it("example1", async () => {
      const response = await getTask1("Riz@z RISO00tto!");
      expect(response.body).toStrictEqual({ msg: "Rizz Risotto" });
    });

    it("example2", async () => {
      const response = await getTask1("alpHa-alFRedo");
      expect(response.body).toStrictEqual({ msg: "Alpha Alfredo" });
    });

    it("error case", async () => {
      const response = await getTask1("");
      expect(response.status).toBe(400);
    });

    it("more filtering and transforming", async () => {
      const response = await getTask1("     mArgheriT4$4a Pi1ZZ4a_ -");
      expect(response.status).toBe(200);
      expect(response.body).toStrictEqual({ msg: "Margherita Pizza"});
    });
  });
});

const clearCookBook = async () => {
  await request("http://localhost:8080").delete("/clear");
};

describe("Task 2", () => {
  beforeEach(clearCookBook);

  describe("POST /entry", () => {
    const putTask2 = async (data) => {
      return await request("http://localhost:8080").post("/entry").send(data);
    };

    
    describe("custom tests", () => {
      it("invalid type", async () => {
        const entry = {
          type: "fake-entry-type",
          name: "BooHoo",
          cookTime: 0
        };

        const resp = await putTask2(entry);
        expect(resp.status).toBe(400);
      });

      it("invalid cookTime", async () => {
        const entry = {
          type: "ingredient",
          name: "BooHoo",
          cookTime: -1
        };

        const response = await putTask2(entry);
        expect(response.status).toBe(400);
      });

      it("mfw requiredItem is the recipe itself", async () => {
        const entry = { type: "recipe", name: "Meatball", requiredItems: [
          { name: "Beef", quantity: 1 },
          { name: "Meatball", quantity: 1 }
        ]}
        const response = await putTask2(entry);
        expect(response.status).toBe(400);
      });

      it("mfw requiredItem occurs again", async () => {
        const entry = { type: "recipe", name: "Meatball", requiredItems: [
          { name: "Beef", quantity: 1 },
          { name: "Beef", quantity: 1 }
        ]}
        const response = await putTask2(entry);
        expect(response.status).toBe(400);
      });

      it("Add Recipe", async () => {
        const meatball = {
          type: "recipe",
          name: "Meatball",
          requiredItems: [{ name: "Beef", quantity: 1 }],
        };
        const resp1 = await putTask2(meatball);
        expect(resp1.status).toBe(200);
      });
    });


    it("Add Ingredients", async () => {
      const entries = [
        { type: "ingredient", name: "Egg", cookTime: 6 },
        { type: "ingredient", name: "Lettuce", cookTime: 1 },
      ];
      for (const entry of entries) {
        const resp = await putTask2(entry);
        expect(resp.status).toBe(200);
        expect(resp.body).toStrictEqual({});
      }
    });

    it("Add Recipe", async () => {
      const meatball = {
        type: "recipe",
        name: "Meatball",
        requiredItems: [{ name: "Beef", quantity: 1 }],
      };
      const resp1 = await putTask2(meatball);
      expect(resp1.status).toBe(200);
    });

    it("Congratulations u burnt the pan pt2", async () => {
      const resp = await putTask2({
        type: "ingredient",
        name: "beef",
        cookTime: -1,
      });
      expect(resp.status).toBe(400);
    });

    it("Congratulations u burnt the pan pt3", async () => {
      const resp = await putTask2({
        type: "pan",
        name: "pan",
        cookTime: 20,
      });
      expect(resp.status).toBe(400);
    });

    it("Unique names", async () => {
      const resp = await putTask2({
        type: "ingredient",
        name: "Beef",
        cookTime: 10,
      });
      expect(resp.status).toBe(200);

      const resp2 = await putTask2({
        type: "ingredient",
        name: "Beef",
        cookTime: 8,
      });
      expect(resp2.status).toBe(400);

      const resp3 = await putTask2({
        type: "recipe",
        name: "Beef",
        cookTime: 8,
      });
      expect(resp3.status).toBe(400);
    });
  });
});

describe("Task 3", () => {
  beforeEach(clearCookBook);
  const postEntry = async (data) => {
    return await request("http://localhost:8080").post("/entry").send(data);
  };

  const getTask3 = async (name) => {
    return await request("http://localhost:8080").get(
      `/summary?name=${name}`
    );
  };

  describe("GET /summary", () => {
    describe("custom", () => {
      it("What is bro doing - Get empty cookbook", async () => {
        const resp = await getTask3("nothing");
        expect(resp.status).toBe(400);
      });
    });

    it("What is bro doing - Get empty cookbook", async () => {
      const resp = await getTask3("nothing");
      expect(resp.status).toBe(400);
    });

    it("What is bro doing - Get ingredient", async () => {
      const resp = await postEntry({
        type: "ingredient",
        name: "beef",
        cookTime: 2,
      });
      expect(resp.status).toBe(200);

      const resp2 = await getTask3("beef");
      expect(resp2.status).toBe(400);
    });

    it("Unknown missing item", async () => {
      const cheese = {
        type: "recipe",
        name: "Cheese",
        requiredItems: [{ name: "Not Real", quantity: 1 }],
      };
      const resp1 = await postEntry(cheese);
      expect(resp1.status).toBe(200);

      const resp2 = await getTask3("Cheese");
      expect(resp2.status).toBe(400);
    });

    it("Bro cooked", async () => {
      const meatball = {
        type: "recipe",
        name: "Skibidi",
        requiredItems: [{ name: "Bruh", quantity: 1 }],
      };
      const resp1 = await postEntry(meatball);
      expect(resp1.status).toBe(200);

      const resp2 = await postEntry({
        type: "ingredient",
        name: "Bruh",
        cookTime: 2,
      });
      expect(resp2.status).toBe(200);

      const resp3 = await getTask3("Skibidi");
      expect(resp3.status).toBe(200);
    });
  });

  describe("custom tests", () => {
    const entries = require('./data/task3_recursion_cookbook.json');

    it("demo recursion", async () => {
      for (const entry of entries) {
        const response = await postEntry(entry);
        expect(response.status).toBe(200);
      }

      const response = await getTask3("Skibidi Spaghetti");
      expect(response.status).toBe(200);
      expect(response.body.cookTime).toBe(46)
      expect(response.body.name).toStrictEqual("Skibidi Spaghetti")

      const ingredients = response.body.ingredients;
      expect(ingredients.length).toBe(4);


      const expected = [
        { "name": "Beef", "quantity": 6 },
        { "name": "Flour", "quantity": 3 },
        { "name": "Egg", "quantity": 4 },
        { "name": "Tomato", "quantity": 2 },
      ];

      const sortFunc = (a, b) => b.name.localeCompare(a.name);
      ingredients.sort(sortFunc);
      expected.sort(sortFunc);
      expect(ingredients).toEqual(expected);
    });
  });

});
