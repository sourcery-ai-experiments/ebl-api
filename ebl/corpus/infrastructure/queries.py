from typing import List, Optional, Sequence

from ebl.corpus.domain.chapter import ChapterId

from ebl.transliteration.infrastructure.collections import (
    CHAPTERS_COLLECTION,
    TEXTS_COLLECTION,
)


def chapter_id_query(id_: ChapterId) -> dict:
    return {
        "textId.genre": id_.text_id.genre.value,
        "textId.category": id_.text_id.category,
        "textId.index": id_.text_id.index,
        "stage": id_.stage.value,
        "name": id_.name,
    }


def join_uncertain_fragments() -> List[dict]:
    return [
        {
            "$unwind": {
                "path": "$uncertainFragments",
                "preserveNullAndEmptyArrays": True,
            }
        },
        {
            "$group": {
                "_id": "$_id",
                "uncertainFragments": {
                    "$push": {
                        "museumNumber": "$uncertainFragments",
                    }
                },
                "root": {"$first": "$$ROOT"},
            }
        },
        {
            "$replaceRoot": {
                "newRoot": {
                    "$mergeObjects": [
                        "$root",
                        {"uncertainFragments": "$uncertainFragments"},
                    ]
                }
            }
        },
        {
            "$set": {
                "uncertainFragments": {
                    "$filter": {
                        "input": "$uncertainFragments",
                        "as": "uncertainFragment",
                        "cond": {
                            "$ne": [
                                {"$type": "$$uncertainFragment.museumNumber"},
                                "missing",
                            ]
                        },
                    }
                }
            }
        },
        {"$project": {"isInFragmentarium": 0}},
    ]


def join_chapters(include_uncertain_fragmnets: bool) -> List[dict]:
    return [
        {
            "$lookup": {
                "from": CHAPTERS_COLLECTION,
                "let": {"genre": "$genre", "category": "$category", "index": "$index"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$textId.genre", "$$genre"]},
                                    {"$eq": ["$textId.category", "$$category"]},
                                    {"$eq": ["$textId.index", "$$index"]},
                                ]
                            }
                        }
                    },
                    {"$addFields": {"firstLine": {"$first": "$lines"}}},
                    {
                        "$project": {
                            "stage": 1,
                            "name": 1,
                            "order": 1,
                            "translation": "$firstLine.translation",
                            "uncertainFragments": 1,
                        }
                    },
                    *(
                        join_uncertain_fragments()
                        if include_uncertain_fragmnets
                        else [{"$project": {"uncertainFragments": 0}}]
                    ),
                    {"$sort": {"order": 1}},
                    {"$project": {"_id": 0, "order": 0}},
                ],
                "as": "chapters",
            }
        },
        {"$project": {"_id": 0}},
    ]


def _match_line_variants(
    lines: Sequence[int],
    variants: Sequence[int],
) -> List[dict]:
    lineVariants = list(map(list, zip(lines, variants)))

    return [
        {"$unwind": {"path": "$lines", "includeArrayIndex": "lineIndex"}},
        {"$match": {"lineIndex": {"$in": lines}}},
        {"$unwind": {"path": "$lines.variants", "includeArrayIndex": "variantIndex"}},
        {"$match": {"$expr": {"$in": [["$lineIndex", "$variantIndex"], lineVariants]}}},
        {
            "$group": {
                "_id": {"_id": "$_id", "lineIndex": "$lineIndex"},
                "id": {"$first": "$id"},
                "manuscripts": {"$first": "$manuscripts"},
                "lines": {"$first": "$lines"},
                "variants": {"$push": "$lines.variants"},
                "record": {"$first": "$record"},
            }
        },
        {
            "$addFields": {
                "lines": {"variants": "$variants"},
            }
        },
        {
            "$group": {
                "_id": {
                    "_id": "$_id._id",
                },
                "id": {"$first": "$id"},
                "manuscripts": {"$first": "$manuscripts"},
                "lines": {"$push": "$lines"},
                "record": {"$first": "$record"},
            }
        },
    ]


def aggregate_chapter_display(
    id_: ChapterId,
    lines: Optional[Sequence[int]],
    variants: Optional[Sequence[int]],
) -> List[dict]:
    return [
        {"$match": chapter_id_query(id_)},
        {
            "$project": {
                "id": {"textId": "$textId", "stage": "$stage", "name": "$name"},
                "lines.number": True,
                "lines.oldLineNumbers": True,
                "lines.isSecondLineOfParallelism": True,
                "lines.isBeginningOfSection": True,
                "lines.translation": True,
                "lines.variants": True,
                "manuscripts": True,
                "record": True,
            }
        },
        *(_match_line_variants(lines, variants) if lines and variants else []),
        {"$project": {"_id": False}},
    ]


def join_text() -> List[dict]:
    return [
        {
            "$lookup": {
                "from": TEXTS_COLLECTION,
                "let": {"textId": "$chapterId.textId"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {
                                        "$eq": [
                                            "$genre",
                                            "$$textId.genre",
                                        ]
                                    },
                                    {
                                        "$eq": [
                                            "$category",
                                            "$$textId.category",
                                        ]
                                    },
                                    {
                                        "$eq": [
                                            "$index",
                                            "$$textId.index",
                                        ]
                                    },
                                ]
                            }
                        }
                    },
                    *join_chapters(False),
                    {"$limit": 1},
                ],
                "as": "text",
            },
        }
    ]


def join_text_title() -> dict:
    return {
        "$lookup": {
            "from": "texts",
            "let": {
                "genre": "$textId.genre",
                "category": "$textId.category",
                "index": "$textId.index",
            },
            "pipeline": [
                {
                    "$match": {
                        "$expr": {
                            "$and": [
                                {"$eq": ["$genre", "$$genre"]},
                                {"$eq": ["$category", "$$category"]},
                                {"$eq": ["$index", "$$index"]},
                            ]
                        }
                    }
                },
                {"$project": {"_id": False, "name": True}},
            ],
            "as": "textName",
        }
    }
