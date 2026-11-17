from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StrictInt

Entry = Annotated[StrictInt, Field(ge=-1_000_000, le=1_000_000)]
Row = Annotated[list[Entry], Field(min_length=2, max_length=2)]
Matrix = Annotated[list[Row], Field(min_length=2, max_length=2)]

class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")

class KeyRequest(Contract):
    key: Matrix = Field(default_factory=lambda: [[3, 3], [2, 5]])

class CipherRequest(KeyRequest):
    text: str = Field(min_length=1, max_length=2000)
    operation: Literal["encrypt", "decrypt"] = "encrypt"

class KeyReport(Contract):
    valid: bool
    determinant: int
    determinant_mod26: int
    gcd: int
    modular_inverse_of_determinant: int | None
    inverse: list[list[int]] | None
    explanation: str

class Letter(Contract):
    letter: str
    number: int

class Term(Contract):
    coefficient: int
    value: int
    product: int

class CalculationRow(Contract):
    terms: list[Term]
    expression: str
    sum: int
    modulus: int
    residue: int
    letter: str

class Block(Contract):
    index: int
    source_block: str
    source_letters: list[Letter]
    source_vector: list[int]
    matrix: list[list[int]]
    rows: list[CalculationRow]
    result_vector: list[int]
    result_block: str

class InverseCheck(Contract):
    product: int
    residue: int

class InverseSteps(Contract):
    valid: bool
    supplied_key: list[list[int]]
    key: list[list[int]]
    a: int
    b: int
    c: int
    d: int
    determinant_expression: str
    determinant: int
    determinant_mod26: int
    gcd: int
    inverse_of_determinant: int
    inverse_check: InverseCheck
    adjugate: list[list[int]]
    scaled_before_modulo: list[list[int]]
    inverse: list[list[int]]
    explanation: str

class CipherResponse(Contract):
    operation: Literal["encrypt", "decrypt"]
    original: str | None = None
    normalized: str | None = None
    padded_plaintext: str | None = None
    padding_added: str | None = None
    padding_count: int | None = None
    removed_characters: str
    letter_map: list[Letter]
    key: list[list[int]]
    blocks: list[Block]
    ciphertext: str
    normalized_ciphertext: str | None = None
    inverse_key: list[list[int]] | None = None
    inverse_steps: InverseSteps | None = None
    plaintext: str | None = None
    padding_note: str | None = None

class Pair(Contract):
    plaintext: str = Field(min_length=2, max_length=2, pattern=r"^[A-Za-z]{2}$")
    ciphertext: str = Field(min_length=2, max_length=2, pattern=r"^[A-Za-z]{2}$")

class RecoveryRequest(Contract):
    pairs: list[Pair] = Field(min_length=2, max_length=30)

class Verification(Pair):
    predicted: str
    matches: bool

class RecoveryResponse(Contract):
    selected_pair_indices: list[int]
    plaintext_matrix: list[list[int]]
    ciphertext_matrix: list[list[int]]
    determinant: int
    determinant_mod26: int
    plaintext_inverse: list[list[int]]
    products: list[list[int]]
    key: list[list[int]]
    verification: list[Verification]

class ExperimentRequest(KeyRequest):
    mode: Literal["fixed", "generated"] = "generated"
    plaintext: str = Field(default="MATRIX", max_length=200)
    count: Annotated[StrictInt, Field(ge=1, le=100)] = 10
    seed: Annotated[StrictInt, Field(ge=0, le=2_147_483_647)] = 42
    length: Annotated[StrictInt, Field(ge=1, le=200)] = 7

class ExperimentRow(Contract):
    id: int
    plaintext: str
    normalized: str
    padded_plaintext: str
    key: list[list[int]]
    ciphertext: str
    recovered: str
    verified: bool

class ExperimentResponse(Contract):
    mode: str
    seed: int
    completed: int
    successful: int
    failed: int
    rows: list[ExperimentRow]
    plaintext_frequency: dict[str, int]
    ciphertext_frequency: dict[str, int]

class SurveyRequest(Contract):
    csv: str = Field(min_length=1, max_length=1_048_576)

class Category(Contract):
    label: str
    count: int
    percentage: float

class SurveyField(Contract):
    name: str
    answered: int
    missing: int
    categories: list[Category]

class SurveyResponse(Contract):
    responses: int
    skipped_empty_rows: int
    fields: list[SurveyField]

class ErrorDetail(Contract):
    field: str
    message: str

class ErrorBody(Contract):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)

class ErrorResponse(Contract):
    error: ErrorBody
