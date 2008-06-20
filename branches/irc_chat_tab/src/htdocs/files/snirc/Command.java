

import java.util.Hashtable;
import java.util.Vector;

/**
 * <p>An rfc1459 command that has been received from the IRC server.
 *
 * @version $Id: Command.java,v 1.4 2004/07/02 23:02:47 bryan_w Exp $
 */
public class Command {
    private static Hashtable commandMap = new Hashtable();
    private static CommandProcessingStrategy defaultStrategy = new DefaultProcess();
    private final String source;
    private final String command;
    private final Vector arguments;
    private final CommandProcessingStrategy strategy;

    public static void registerStrategies() {
        new NamesNumericsStrategy().register();
        new SimpleNumericsStrategy().register();
        new ChannelJoinPartStrategy().register();
        new ModeStrategy().register();
        new PrivmsgStrategy().register();
        new NoticeStrategy().register();
        new NickCommandsStrategy().register();
    }

    public static void registerStrategy(String commandName, CommandProcessingStrategy strategy) {
        commandMap.put(commandName, strategy);
    }

    public static Command parseLine(String line) {
        if (line.length() == 0)
            return null;

        // Using a StringTokenizer here seems like using the corner of
        // a flat-headed screwdriver on a phillips screw. It'd work,
        // but it's still the Wrong Tool. So we go for ugly instead.

        String nextToken = null;
        String source = null;
        java.util.Vector arguments = new java.util.Vector();

        int pos = 0;
        int start = -1;

        if (line.charAt(0) == ':') {
            pos = line.indexOf(' ');
            source = line.substring(1, pos);
        }

        for (; pos < line.length(); pos++) {
            if (line.charAt(pos) == ' ') {
                if (start != -1)
                    break;
                else
                    continue;
            }

            if (start == -1)
                start = pos;
        }
        if (start == -1)
            return null;

        String commandName = line.substring(start, pos);

        while (pos < line.length()) {
            start = -1;

            for (; pos < line.length(); pos++) {
                if (line.charAt(pos) == ' ') {
                    if (start != -1)
                        break;
                    else
                        continue;
                }

                if ((line.charAt(pos) == ':') && (start == -1)) {

                    start = pos + 1;
                    pos = line.length() - 1;

                    while (line.charAt(pos) == ' ') {
                        pos--;
                    }
                }

                if (start == -1)
                    start = pos;
            }
            if (start != -1) {
                arguments.addElement(line.substring(start, pos));
            }
        }
        if (commandMap.containsKey(commandName.toUpperCase()))
            return new Command((CommandProcessingStrategy) commandMap.get(commandName.toUpperCase()), source, commandName, arguments);

        return new Command(defaultStrategy, source, commandName, arguments);
    }

    public Command(CommandProcessingStrategy strategy, String source, String command, Vector arguments) {
        this.strategy = strategy;
        this.source = source;
        this.command = command;
        this.arguments = arguments;
    }

    public void execute(Chat session) {
        strategy.execute(this, session);
    }

    public String getArgument(int index) {
        if (index >= arguments.size())
            return null;

        return (String) arguments.elementAt(index);
    }

    public String getArguments() {
        return getArguments(0);
    }

    public String getArguments(int firstArgument) {
        StringBuffer buf = new StringBuffer();
		buf.append(" ");
        for (int i = firstArgument; i < arguments.size(); i++) {
            if (i > firstArgument)
                buf.append(' ');
            buf.append((String) arguments.elementAt(i));
        }

        return buf.toString();
    }

    public String getCommand() {
        return command;
    }

    public String getFullSource() {
        return source;
    }

    public String getSource() {
      try {
        if (source.indexOf('!') != -1)
            return source.substring(0, source.indexOf('!'));
        return source;
      } catch (NullPointerException e) {
        System.out.println("Null Pointer Excecption Ignored");
      }
      return "";
    }

    public void stripColoursFromLastArgument() {
        String source = (String) arguments.lastElement();
        StringBuffer buf = new StringBuffer(source.length());

        boolean inColourCode = false;
        int numberCount = 0;
        int commaCount = 0;

        for (int i = 0; i < source.length(); i++) {
            if (inColourCode) {
                if (source.charAt(i) == ',') {
                    numberCount = 0;
                    commaCount++;
                    if (commaCount <= 1)
                        continue;
                }

                if (Character.isDigit(source.charAt(i))) {
                    numberCount++;
                    if (numberCount <= 2)
                        continue;
                }

                commaCount = 0;
                numberCount = 0;
                inColourCode = false;
            }

            if (source.charAt(i) == '\003') {
                inColourCode = true;
                continue;
            }

            buf.append(source.charAt(i));
        }

        arguments.setElementAt(buf.toString(), arguments.size() - 1);
    }
}
