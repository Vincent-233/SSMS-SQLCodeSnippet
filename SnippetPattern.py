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
WHERE name LIKE '%%'
order by modify_date DESC;
"""

sft = """-- search tables
SELECT * FROM sys.tables
WHERE name LIKE '%%'
order by modify_date DESC;
"""

sff = """-- search functions
SELECT * FROM sys .objects WHERE type IN ( 'IF', 'TF', 'FN')
AND name LIKE '%%';
"""

sfp = """-- search procedures
SELECT * FROM sys.procedures
WHERE name LIKE '%%'
order by modify_date DESC;
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

long_query = """-- Execute the query inside target database
SELECT TOP 10
      qs.total_elapsed_time / qs.execution_count / 1000000.0 AS average_seconds,
      qs.total_elapsed_time / 1000000.0 AS total_seconds,
      qs.execution_count,
      SUBSTRING (qt.text,qs.statement_start_offset/2, 
      (CASE WHEN qs.statement_end_offset = -1 
      THEN LEN(CONVERT(NVARCHAR(MAX), qt.text)) * 2 
      ELSE qs.statement_end_offset END - qs.statement_start_offset)/2) AS individual_query,
      o.name AS object_name,
      DB_NAME(qt.dbid) AS database_name
FROM
      sys.dm_exec_query_stats qs
      CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) as qt
      LEFT OUTER JOIN sys.objects o ON qt.objectid = o.object_id
WHERE 
      qt.dbid = DB_ID()
ORDER BY 
      average_seconds DESC;
"""


running_query = """-- Running Query
SELECT req.session_id
	,s.login_time
	,req.start_time
	,req.total_elapsed_time
	,req.total_elapsed_time / 1000.0 / 60.0 AS total_eplapsed_minutes
	,req.STATUS
	,req.command
	,req.database_id
       ,req.last_wait_type
       ,req.blocking_session_id
	,db.name AS [database]
	,object_name(st.objectid, st.[dbid]) 'ObjectName'
	,s.login_name
	,s.host_name
	,s.program_name
	,s.client_version
	,s.nt_user_name
	,req.open_transaction_count
	,req.estimated_completion_time
	,st.TEXT
	,SUBSTRING(ST.TEXT, (req.statement_start_offset / 2) + 1, (
			(
				CASE statement_end_offset
					WHEN - 1
						THEN DATALENGTH(ST.TEXT)
					ELSE req.statement_end_offset
					END - req.statement_start_offset
				) / 2
			) + 1) AS statement_text
FROM sys.dm_exec_requests req
CROSS APPLY sys.dm_exec_sql_text(req.sql_handle) AS st
LEFT JOIN sys.databases db ON req.database_id = db.database_id
LEFT JOIN sys.dm_exec_sessions s ON req.session_id = s.session_id;
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
    {'title':'restore history' ,'description':'show restore history', 'sql':restore_history},
    {'title':'long query' ,'description':'show long run query', 'sql':long_query},
    {'title':'running query' ,'description':'show running query', 'sql':running_query}
]


         






















