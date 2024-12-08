#!/bin/bash

# Проверяем наличие двух аргументов
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <reference_path> <reads_path>"
  exit 1
fi

# Пути к файлам
REFERENCE_PATH="$1"
READS_PATH="$2"

# Шаг 1: Запуск FastQC
echo "Running FastQC..."
fastqc "$READS_PATH"

# Шаг 2: Индексация референсного генома
echo "Indexing reference genome..."
bwa index "$REFERENCE_PATH"

# Шаг 3: Картирование ридов на референсный геном
echo "Aligning reads..."
bwa mem "$REFERENCE_PATH" "$READS_PATH" > aligned.sam

# Шаг 4: Анализ выравнивания
echo "Running samtools flagstat..."
FLAGSTAT_OUTPUT=$(samtools flagstat aligned.sam)

# Шаг 5: Поиск процента картированных ридов
echo "Analyzing mapping percentage..."
MAPPED_PERCENTAGE=$(echo "$FLAGSTAT_OUTPUT" | grep -m1 -oP -c=0 'mapped \(\K[\d.]+(?=%)')

if [ -n "$MAPPED_PERCENTAGE" ]; then
  if (( $(echo "$MAPPED_PERCENTAGE > 90.0" | bc -l) )); then
    echo "OK: mapped ${MAPPED_PERCENTAGE}%"
  else
    echo "not OK: mapped ${MAPPED_PERCENTAGE}%"
  fi
else
  echo "No mapped percentage found"
fi