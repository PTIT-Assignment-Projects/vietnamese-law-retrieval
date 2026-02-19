<h2><a href="https://github.com/Nayjest/Gito"><img src="https://raw.githubusercontent.com/Nayjest/Gito/main/press-kit/logo/gito-bot-1_64top.png" align="left" width=64 height=50 title="Gito v4.0.3"/></a>I've Reviewed the Code</h2>

The code review of the `TextProcessor` class in `text_processor.py` reveals an inconsistent character set in the regular expression pattern, which can be improved for better consistency and readability, but does not demonstrate exceptional achievements worthy of an award.

**⚠️ 1 issue found** across 1 file
## `#1`  Inconsistent Character Set in Regular Expression Pattern
[src/preprocessing/text_processor.py L20](https://github.com/PTIT-Assignment-Projects/vietnamese-law-retrieval/blob/main/src/preprocessing/text_processor.py#L20)

    
The regular expression pattern is using a mix of Unicode characters and escaped characters. To maintain consistency, it is better to use either Unicode characters or escaped characters throughout the pattern.
**Tags: naming, code-style**
**Affected code:**
```python
20:             r"^[a-z0-9_àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ.\-]+$"
```
**Proposed change:**
```python
            valid_pattern = re.compile(
                r"^[a-z0-9_\u00E0-\u01FF\u1EA0-\u1EFF.-]+$"
            )
```
<!-- GITO_COMMENT:CODE_REVIEW_REPORT -->