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
SELECT OBJECT_NAME(a.object_id),b.modify_date,a.* 
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
    p.partition_number,
    p.rows AS RowCounts,
    CAST(ROUND((SUM(a.used_pages) / 128.00), 2) AS NUMERIC(36, 2)) AS Used_MB,
    CAST(ROUND((SUM(a.total_pages) - SUM(a.used_pages)) / 128.00, 2) AS NUMERIC(36, 2)) AS Unused_MB,
    CAST(ROUND((SUM(a.total_pages) / 128.00), 2) AS NUMERIC(36, 2)) AS Total_MB
    FROM sys.tables t
    INNER JOIN sys.indexes i ON t.OBJECT_ID = i.object_id
    INNER JOIN sys.partitions p ON i.object_id = p.OBJECT_ID AND i.index_id = p.index_id
    INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
    INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
GROUP BY t.Name, s.Name, p.Rows, p.partition_number
ORDER BY Total_MB DESC;
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
    ,req.wait_resource
    ,req.blocking_session_id AS blocking_by_session_id
    ,db.name AS [database]
    ,object_name(st.objectid, st.[dbid]) 'ObjectName'
    ,s.login_name
    ,s.host_name
    ,s.program_name
    ,s.client_version
    ,s.nt_user_name
    ,req.open_transaction_count
    ,req.estimated_completion_time
    ,DATALENGTH(ST.TEXT) AS statement_length
    ,req.statement_start_offset
    ,req.statement_end_offset
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


insert_select = """--- Insert Select Query
DECLARE @Table VARCHAR(500) = '<TableName>';
DECLARE @Cols VARCHAR(MAX),@Inser_Select VARCHAR(MAX);
SET @Cols = ',' + (
    SELECT  name + CHAR(10) + ','
    FROM sys.columns
    WHERE OBJECT_ID = OBJECT_ID(@Table)
    FOR XML PATH('')
)
SET @Cols =  REPLACE(LEFT(@Cols,LEN(@Cols )-1),',','    ,')
SET @Cols = '     ' + RIGHT(@Cols,LEN(@Cols)-5)
SET @Inser_Select = 'INSERT INTO '+@Table+CHAR(10)+'('+CHAR(10)+@Cols+')'+CHAR(10)+'SELECT'+CHAR(10)+@Cols+'FROM '+ @Table + ';'
PRINT @Inser_Select;
"""


partition_info = """-- 分区表数据分布情况
SELECT  OBJECT_NAME(i.object_id) AS ObjectName
       ,c.name AS PartitioningColumn
       ,CONVERT(VARCHAR(50), ps.name) AS partition_scheme
       ,p.partition_number
       ,CONVERT(VARCHAR(10), ds2.name) AS filegroup
       ,CONVERT(VARCHAR(19), ISNULL(v.value, ''), 120) AS range_boundary
       ,p.rows
       --,df.physical_name AS DatabaseFileName
FROM    sys.indexes i
        JOIN sys.partition_schemes ps ON i.data_space_id = ps.data_space_id
        JOIN sys.destination_data_spaces dds ON ps.data_space_id = dds.partition_scheme_id
        JOIN sys.data_spaces ds2 ON dds.data_space_id = ds2.data_space_id
        JOIN sys.partitions p ON dds.destination_id = p.partition_number AND p.object_id = i.object_id AND p.index_id = i.index_id
        JOIN sys.partition_functions pf ON ps.function_id = pf.function_id
        --JOIN sys.database_files df ON df.data_space_id = ds2.data_space_id
        JOIN sys.index_columns AS ic ON ic.[object_id] = i.[object_id] AND ic.index_id = i.index_id AND ic.partition_ordinal >= 1 
        JOIN sys.columns AS c ON i.[object_id] = c.[object_id] AND ic.column_id = c.column_id
        LEFT JOIN sys.partition_range_values v ON pf.function_id = v.function_id AND v.boundary_id = p.partition_number - pf.boundary_value_on_right
WHERE   i.index_id IN (0, 1) -- Heap and Clustered Index
ORDER BY ObjectName,partition_number
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
    {'title':'running query' ,'description':'show running query', 'sql':running_query},
    {'title':'insert select' ,'description':'insert ... select from ...', 'sql':insert_select},
    {'title':'partition info' ,'description':'partition table information', 'sql':partition_info}
]


         






















