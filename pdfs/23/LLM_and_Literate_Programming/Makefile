.PHONY: all clean

# Default target
all: Literate_Programming_Experiment_with_GPT4.pdf

# Main file: combine artile with appendix
Literate_Programming_Experiment_with_GPT4.pdf: Literate_Programming_Experiment_with_GPT4.article.pdf Literate_Programming_Experiment_with_GPT4-Appendix-Dialog.dialog.pdf
	# Concatenate the input PDF files into the main PDF
	pdftk $^ cat output $@

# Rule to generate the dialog PDF file
# Due to imperfect formatting going Markdown to PDF
# via pandoc+latex triggers many errors
# so I ended up just numbering text lines
# which actually maybe better anyway.
Literate_Programming_Experiment_with_GPT4-Appendix-Dialog.dialog.pdf: Literate_Programming_Experiment_with_GPT4-Appendix-Dialog.dialog.ps
	# Convert the PS file to PDF
	ps2pdf "$<" "$@"

# Rule to generate the dialog PS file
Literate_Programming_Experiment_with_GPT4-Appendix-Dialog.dialog.ps: Literate_Programming_Experiment_with_GPT4-Appendix-Dialog.dialog.md
	# Generate the PS file with line numbers using Vim
	vim -c 'set printoptions=number:y' -c "hardcopy > $@" -c quit "$<"

%.pdf: %.latex
	# Generate the PDF from LaTeX using pdflatex
	pdflatex "$<" && rm $(basename $@).log && rm $(basename $@).aux

%.latex: %.md
	# Convert Markdown to LaTeX using Pandoc
	pandoc --listings -s -o "$@" "$<"

# Clean target to remove generated files
clean:
	# Remove all generated files
	rm -f *.aux *.log *.pdf *.latex *.ps

