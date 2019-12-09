snippet_pattern = """<?xml version="1.0" encoding="utf-8" ?>
<CodeSnippets xmlns="http://schemas.microsoft.com/VisualStudio/2005/CodeSnippet">
<_locDefinition xmlns="urn:locstudio">
    <_locDefault _loc="locNone" />
    <_locTag _loc="locData">Title</_locTag>
    <_locTag _loc="locData">Description</_locTag>
    <_locTag _loc="locData">Author</_locTag>
    <_locTag _loc="locData">ToolTip</_locTag>
</_locDefinition>
	<CodeSnippet Format="1.0.0">
	<Header>
	<Title>{title}</Title>
        <Shortcut></Shortcut>
	<Description>{description}</Description>
	<Author>God</Author>
	<SnippetTypes>
		<SnippetType>Expansion</SnippetType>
	</SnippetTypes>
	</Header>
	<Snippet>
		<Declarations>
		</Declarations>
		<Code Language="SQL">
			<![CDATA[{sql}]]>
		</Code>
	</Snippet>
	</CodeSnippet>
</CodeSnippets>
"""

depends = """-- 查询依赖（字符依赖，注释都算）【sql_modules】
SELECT OBJECT_NAME(a.object_id),a.* 
FROM sys.sql_modules a
INNER JOIN sys.objects b ON a.object_id = b.object_id
WHERE CHARINDEX('',a.definition) > 0
  AND b.type = 'P';
"""

sfv = """-- search views
SELECT * FROM sys.views
WHERE name LIKE '%%';
"""

sft = """-- search tables
SELECT * FROM sys.tables
WHERE name LIKE '%%';
"""

sff = """-- search functions
SELECT * FROM sys .objects WHERE type IN ( 'IF', 'TF', 'FN')
AND name LIKE '%%';
"""

sfp = """-- search procedures
SELECT * FROM sys.procedures
WHERE name LIKE '%%';
"""

sfc = """-- search column names
SELECT a.name AS column_name,c.name AS data_type,b.name AS [object_name],b.[type_desc] AS object_type
FROM sys.columns a
INNER JOIN sys.objects b ON a.object_id = b.object_id
INNER JOIN sys.types c ON a.system_type_id = c.user_type_id
WHERE b.Type IN ('U','V') 
  AND a.name LIKE '%%';
"""

table_size = """SELECT
s.Name AS SchemaName,
t.Name AS TableName,
p.rows AS RowCounts,
CAST(ROUND((SUM(a.used_pages) / 128.00), 2) AS NUMERIC(36, 2)) AS Used_MB,
CAST(ROUND((SUM(a.total_pages) - SUM(a.used_pages)) / 128.00, 2) AS NUMERIC(36, 2)) AS Unused_MB,
CAST(ROUND((SUM(a.total_pages) / 128.00), 2) AS NUMERIC(36, 2)) AS Total_MB
FROM sys.tables t
INNER JOIN sys.indexes i ON t.OBJECT_ID = i.object_id
INNER JOIN sys.partitions p ON i.object_id = p.OBJECT_ID AND i.index_id = p.index_id
INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
GROUP BY t.Name, s.Name, p.Rows
ORDER BY Total_MB desc;
"""

backup_history = """-- 查询所有数据库备份历史（在此基础上可以做其他改进，如查最后一次备份日期等）
SELECT
        a.database_name
       ,b. physical_device_name
       ,a. [type]    -- D-Database | I-Differential database | L-Log | F-File or filegroup   
       ,a. [user_name]
       ,a. server_name
       ,a. machine_name
       ,a. compatibility_level
       ,a. backup_start_date
       ,a. backup_finish_date
       ,LTRIM( ROUND(CAST (a. backup_size AS FLOAT)/( 1024*1024 ),2)) + ' MB' backup_size
       ,LTRIM( ROUND(CAST (a. compressed_backup_size AS FLOAT)/(1024 *1024), 2)) + ' MB' compressed_backup_size
       ,a. name Remark
FROM
       msdb..backupset a
LEFT JOIN
       msdb..backupmediafamily b ON a .media_set_id = b .media_set_id
--WHERE
--	CHARINDEX('DTC',a.database_name) > 0
ORDER BY
       backup_finish_date DESC;
"""

restore_history = """-- 还原历史
SELECT
       a.destination_database_name
       ,c. destination_phys_name
       ,a. [user_name]
       ,a. restore_type
       ,a. [replace]
       ,b. name file_back_name
       ,b. backup_finish_date File_backup_date
       ,a. restore_date
	   ,c .file_number
FROM msdb ..restorehistory a
INNER JOIN msdb.. backupset b ON a. backup_set_id = b . backup_set_id
INNER JOIN msdb.. restorefile c ON a. restore_history_id = c.restore_history_id
WHERE c .file_number = 1 -- mdf file 
ORDER BY b. backup_finish_date DESC;
"""


# snippets 的结构配置
snippets = [
    {'title':'depends' ,'description':'search words from definition', 'sql':depends},
    {'title':'sfv' ,'description':'search views', 'sql':sfv},
    {'title':'sft' ,'description':'search tables', 'sql':sft},
    {'title':'sff' ,'description':'search functions', 'sql':sff},
    {'title':'sfp' ,'description':'search procedures', 'sql':sfp},
    {'title':'sfc' ,'description':'search column names', 'sql':sfc},
    {'title':'table sizes' ,'description':'show table rows and sizes', 'sql':table_size},
    {'title':'backup history' ,'description':'show backup history', 'sql':backup_history},
    {'title':'restore history' ,'description':'show restore history', 'sql':restore_history}
]


         






















